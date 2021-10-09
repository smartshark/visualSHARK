<template>
  <div class="wrapper">
  <template v-if="flashes">
    <b-alert v-for="flash in flashes" :key="flash.id" placement="top-center" duration="5" variant="success" dismissable>
      <span class="icon-info-circled alert-icon-float-left"></span>
      <p>{{flash.message}}</p>
    </b-alert>
  </template>

    <div class="animated fadeIn">
      <div class="clearfix"></div>
      <div class="card">
        <div class="card-header">
          <i class="fa fa-cog"></i> Control View
        </div>
        <div class="card-block">
            This view shows the labels you assigned for each line for a specific issue. The issue can be selected in the <router-link :to="{ name: 'Corrections'}">corrections overview</router-link>.
        </div>
      </div>
      <div class="card">
            <div class="card-header">
              <i class="fa fa-tag"></i> Labels
            </div>
            <div class="card-block">
                <div class="label" data-toggle="tooltip" data-placement="top" title="The line contributes to the corrective change that is performed to address the issue that is described."><span class="dot" style="background-color: #FF0000;">1</span>bug fix</div>
                <div class="label" data-toggle="tooltip" data-placement="top" title="The line only contains changes to whitespaces that do not affect the logic of the source code."><span class="dot">2</span>whitespace</div>
                <div class="label" data-toggle="tooltip" data-placement="top" title="The line only contains changes to documentation of the software, including line comments or documentation files."><span class="dot" style="background-color: #442727;">3</span>documentation</div>
                <div class="label" data-toggle="tooltip" data-placement="top" title="The change is a refactoring, e.g., a renaming of a variable or the extraction of a method."><span class="dot" style="background-color: #0779e4;">4</span>refactoring</div>
                <div class="label" data-toggle="tooltip" data-placement="top" title="The change is only to tests of the project, e.g., test code or test data."><span class="dot" style="background-color: #00FF00;">5</span>test</div>
                <div class="label" data-toggle="tooltip" data-placement="top" title="The change is neither of the above, e.g., the addition of features unrelated to the described issue."><span class="dot" style="background-color: #ffbd69;">6</span>unrelated</div>
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

<div class="col-sm-10">{{ issue.title }}
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
              <div v-for="c in commits">
                <MonacoCommitDiffView :commit="c" :vcs_url="vcs_url" ref="commitDiffView" />
              </div>
          </div>

  </div>
</template>

<script>
import { mapGetters } from 'vuex'
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
        external_id: ''
      }
    },
    props: {
      loadExternalId: String
    },
    computed: mapGetters({
        currentProject: 'currentProject',
        projectsVcs: 'projectsVcs',
        projectsIts: 'projectsIts',
        projectsMl: 'projectsMl'
    }),
    mounted() {
      if(typeof this.loadExternalId !== 'undefined') {
        this.loadIssue(this.loadExternalId)
      }
    },
    components: {
        MonacoCommitDiffView
    },
    methods: {
        loadIssueReload: function() {
          if(this.external_id) {
            this.$router.push('/labeling/lineControl/' + this.external_id)
            setTimeout(() => {
              window.location.reload(false);
            }, 25)
          }
        },
        loadIssue: function(external_id) {
            this.$store.dispatch('pushLoading')
            rest.getIssueForControl(external_id)
            .then(response => {
                this.$store.dispatch('popLoading')

                window.commits = response.data['commits'];
                this.commits = response.data['commits'];
                this.issue = response.data['issue'];
                this.vcs_url = response.data['vcs_url']
                this.issue_url = response.data['issue_url']
                this.all = response.data['all']
                this.corrected = response.data['corrected']
                this.skipped = response.data['skipped']

                setTimeout(() => {
                    // Register all editors
                    this.registerFoldingModel();
                    for(var i = 0; i < this.$refs.commitDiffView.length; i++)
                    {
                    this.$refs.commitDiffView[i].initEditors();
                    }
                    this.validateAll();
                }, 25);
            })
            .catch(e => {
                this.$store.dispatch('pushError', e)
            });
        },
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
            monaco.languages.registerFoldingRangeProvider("java", {  // eslint-disable-line no-undef
                provideFoldingRanges: function(model, context, token) {  //eslint-disable-line no-unused-vars
                    var margin = 2;
                    var ranges = [];
                    // Detect editor
                    var editor = null;
                    var editors = that.getEditors();
                    for (let i = 0; i < editors.length; i++) {
                        var currentEditor = editors[i].getEditor();
                        if (currentEditor.getOriginalEditor().getModel() == model) {
                            editor = currentEditor;
                        } else if (currentEditor.getModifiedEditor().getModel() == model) {
                            editor = currentEditor;
                        }
                    }
                    var startLine = 1;
                    var changes = editor.getLineChanges();
                    for (let i = 0; i < changes.length; i++) {
                        var change = changes[i];
                        var ende = change.originalStartLineNumber;
                        if (ende > change.modifiedStartLineNumber) {
                            ende = change.modifiedStartLineNumber;
                        }
                        ende = ende - margin;
                        var range = {
                            start: startLine,
                            end: ende,
                            kind: monaco.languages.FoldingRangeKind.Region  // eslint-disable-line no-undef
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
                        kind: monaco.languages.FoldingRangeKind.Region  // eslint-disable-line no-undef
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
.bugfix-pre {
  width: 5px !important;
  background-color: #FF0000;
}
.whitespace-pre {
  width: 5px !important;
  background-color: #bbb;
}
.documentation-pre {
  width: 5px !important;
  background-color:#442727;
}
.test-pre {
  width: 5px !important;
  background-color: #00FF00;
}
.refactoring-pre {
  width: 5px !important;
  background-color: #0779e4;
}
.unrelated-pre {
  width: 5px !important;
  background-color: #ffbd69;
}
pre.force-wrap {
  white-space: pre-wrap;       /* Since CSS 2.1 */
  white-space: -moz-pre-wrap;  /* Mozilla, since 1999 */
  white-space: -pre-wrap;      /* Opera 4-6 */
  white-space: -o-pre-wrap;    /* Opera 7 */
  word-wrap: break-word;       /* Internet Explorer 5.5+ */
}
</style>
