<template>
  <div class="wrapper">
  <template v-if="flashes">
    <alert v-for="flash in flashes" :key="flash.id" placement="top-center" duration="5" type="success" dismissable>
      <span class="icon-info-circled alert-icon-float-left"></span>
      <p>{{flash.message}}</p>
    </alert>
  </template>

    <div class="animated fadeIn">
<div v-if="error.length > 0">
    <alert placement="top-center" duration="5" type="warning">
          <ul>
             <li v-for="item in error">
                Missing labels in commit {{ item.parent_revision_hash }}, file {{ item.filename }}
                <button class="btn btn-primary btn-xs" v-on:click="jumpToChange(item)">Jump to</button>
            </li>
          </ul>
    </alert>
        </div>
            <button class="btn btn-primary" v-on:click="submitLabels()" style="float: right; margin-bottom: 5px;">Submit labels</button>
            <div class="clearfix"></div>
     <div class="card">
            <div class="card-header">
              <i class="fa fa-tag"></i> Labels
            </div>
            <div class="card-block">
                <div class="label"><span class="dot" style="background-color: #FF0000;">1</span>bug fix</div>
                <div class="label"><span class="dot">2</span>whitespace</div>
                <div class="label"><span class="dot" style="background-color: #442727;">3</span>documentation</div>
                <div class="label"><span class="dot" style="background-color: #0779e4;">4</span>refactoring</div>
                <div class="label"><span class="dot" style="background-color: #00FF00;">5</span>test</div>
                <div class="label"><span class="dot" style="background-color: #ffbd69;">6</span>unrelated</div>
                <div class="label"><span class="dot" style="background-color: #fff; color:#000; border: #000 solid 1px;">7</span>remove current label</div>
                <div>Press the key of the color to label the current line with the belonging label, press 7 to remove the label</div>
            </div>
      </div>
          <div class="card">
            <div class="card-header">
              <i class="fa fa-bug"></i> <a :href="issue_url + issue.external_id" target="_blank">{{issue.external_id}}</a> - {{issue.title}}
            </div>
            <div class="card-block">
            <div class="row">
<label class="col-sm-2">Issue title</label>

<div class="col-sm-10">
            <a href="#">{{ issue.title }}</a>
            </div>
            </div>


<div class="row">
<label class="col-sm-2">Issue description</label>
<div class="col-sm-10">
             <pre class="force-wrap">{{ issue.desc }}</pre>
            </div>
            </div>
                        <div class="row">
<label class="col-sm-2">Commits</label>
<div class="col-sm-10">
            <button v-for="commit in commits" v-on:click="scrollToCommit(commit)" class="btn btn-default" style="margin-right: 5px;">{{ commit.revision_hash }}</button>
            </div>
            </div>
            </div>
          </div>
              <template v-for="c in commits">
                <MonacoCommitDiffView :commit="c" ref="commitDiffView" />
              </template>
          </div>

    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { alert } from 'vue-strap'
import rest from '../api/rest'
import MonacoCommitDiffView from '@/components/MonacoCommitDiffView.vue'

export default {
    data() {
        return {
            commits: [],
            issue: '',
            flashes: [],
            error: [],
      vcs_url: '',
      issue_url: '',
        }
    },
    computed: mapGetters({
        currentProject: 'currentProject',
        projectsVcs: 'projectsVcs',
        projectsIts: 'projectsIts',
        projectsMl: 'projectsMl'
    }),
    mounted() {

        var that = this;

        // Start background request
        this.$store.dispatch('pushLoading')
        rest.getIssueWithCommits(this.currentProject.name)
            .then(response => {
                this.$store.dispatch('popLoading')

                 // maybe we are finished for this project
                if(response.data['warning'] == 'no_more_issues') {
                    this.flashes.push({id: 'no_more_issues', message: 'No more issues for this project available, select next project.'})
                    return
                }

                window.commits = response.data['commits'];
                this.commits = response.data['commits'];
                this.issue = response.data['issue'];
                this.vcs_url = response.data['vcs_url']
                this.issue_url = response.data['issue_url']
                setTimeout(() => {
                    // Register all editors
                    that.registerFoldingModel();
                    for(var i = 0; i < that.$refs.commitDiffView.length; i++)
                    {
                    that.$refs.commitDiffView[i].initEditors();
                    }
                    that.validateAll();
                }, 25);

                if(this.has_trained !== true) {
                    this.flashes.push({id: 'train', message: 'You have not finished the training! Loading training issues first!'})
                }

                if(this.load_last === true) {
                     this.flashes.push({id: 'last', message: 'You have not finished labeling the last issue, loading last issue first.'})
                }
            })
            .catch(e => {
                this.$store.dispatch('pushError', e)
            });
    },
    components: {
        MonacoCommitDiffView,
        alert
    },
    methods: {
        scrollToCommit : function(commit) {
            document.getElementById('collapse' + commit.revision_hash).style.display = "block";
            document.getElementById(commit.revision_hash).scrollIntoView();
        },
        jumpToChange : function(change)
        {
            document.getElementById('file' + change.filename + change.parent_revision_hash).scrollIntoView();
        },
        getEditors : function() {
           var editors = [];
           for(var i = 0; i < this.$refs.commitDiffView.length; i++)
           {
           editors = editors.concat(this.$refs.commitDiffView[i].getEditors());
           }
           return editors;
        },
        registerFoldingModel: function() {
            var that = this;
            monaco.languages.registerFoldingRangeProvider("java", {
                provideFoldingRanges: function(model, context, token) {
                    var margin = 2;
                    var ranges = [];
                    // Detect editor
                    var editor = null;
                    var isOrginial = false;
                    var editors = that.getEditors();
                    for (var i = 0; i < editors.length; i++) {
                        var currentEditor = editors[i].getEditor();
                        if (currentEditor.getOriginalEditor().getModel() == model) {
                            editor = currentEditor;
                            isOrginial = true;
                        } else if (currentEditor.getModifiedEditor().getModel() == model) {
                            editor = currentEditor;
                            isOrginial = false;
                        }
                    }
                    var startLine = 1;
                    var changes = editor.getLineChanges();
                    for (var i = 0; i < changes.length; i++) {
                        var change = changes[i];
                        var ende = change.originalStartLineNumber;
                        if (ende > change.modifiedStartLineNumber) {
                            ende = change.modifiedStartLineNumber;
                        }
                        ende = ende - margin;
                        var range = {
                            start: startLine,
                            end: ende,
                            kind: monaco.languages.FoldingRangeKind.Region
                        };
                        ranges.push(range);

                        var newStartLine = change.originalEndLineNumber;
                        if (newStartLine < change.modifiedEndLineNumber) {
                            newStartLine = change.modifiedEndLineNumber;
                        }
                        if (newStartLine == 0) {
                            newStartLine = ende + 1;

                        }
                        startLine = newStartLine + margin;

                    }

                    ranges.push({
                        start: startLine + margin,
                        end: model.getLineCount(),
                        kind: monaco.languages.FoldingRangeKind.Region
                    });
                    return ranges;
                }
            });
        },
        validateAll: function () {
            var that = this;
            setTimeout(() => {
                    for (var i = 0; i < that.$refs.commitDiffView.length; i++) {
                        that.$refs.commitDiffView[i].validate()
                    }
             }, 1000);
        },
        submitLabels : function() {
             // check if anything is missing
             var correct = [];
             for (var i = 0; i < this.$refs.commitDiffView.length; i++) {
                  correct = correct.concat(this.$refs.commitDiffView[i].validate());
                  this.$refs.commitDiffView[i].showValidation(true);
             }
             this.error = correct;
             console.log(this.error);
             if(correct.length > 0)
             {
                window.alert("Some labels are missing");
                return;
             }
             // else collect data for transmit
             var data = {};
             for (var i = 0; i < this.$refs.commitDiffView.length; i++) {
                 data = Object.assign({}, data, this.$refs.commitDiffView[i].getData());
             }

            console.log(data);
            this.$store.dispatch('pushLoading')
            var result = {labels : data, issue_id: this.issue.id}
            rest.saveLabelsOfCommits({ data : result, 'type': 'old_new' })
            .then(response => {
                this.$store.dispatch('popLoading');
                window.location.replace(window.location.pathname + window.location.search + window.location.hash);
            })
            .catch(e => {
                this.$store.dispatch('pushError', e)
            });
        }
    }
}
</script>

<style>
.editor {
  width: 100% !important;
  height: 800px;
}

.header-valid {
  background-color: #57e84b;
}

.label {
display: inline-flex;
align-items: center;
margin-right: 10px;
}
.dot {
  margin: 2px;
  height: 25px;
  width: 25px;
  background-color: #bbb;
  border-radius: 50%;
  display: inline-block;
  color: white;
  text-align: center;
  padding-top: 2px;
}

.bugfix {
	background: #FF0000;
	width: 5px !important;
	margin-left: 3px;
}
.whitespace {
  background-color: #bbb;
	width: 5px !important;
	margin-left: 3px;
}
.documentation {
  background-color: #442727;
	width: 5px !important;
	margin-left: 3px;
}
.test {
  background-color: #00FF00;
	width: 5px !important;
	margin-left: 3px;
}
.refactoring {
  background-color: #0779e4;
	width: 5px !important;
	margin-left: 3px;
}
.unrelated {
  background-color: #ffbd69;
	width: 5px !important;
	margin-left: 3px;
}
pre.force-wrap {
  white-space: pre-wrap;       /* Since CSS 2.1 */
  white-space: -moz-pre-wrap;  /* Mozilla, since 1999 */
  white-space: -pre-wrap;      /* Opera 4-6 */
  white-space: -o-pre-wrap;    /* Opera 7 */
  word-wrap: break-word;       /* Internet Explorer 5.5+ */
}
</style>
