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
          <i class="fa fa-tag"></i> Most used technologies
        </div>
        <div class="card-block">
          TAG CLOUD: <template v-for="tech in technologies">{{tech}}&nbsp;</template>
        </div>
      </div>
      <template v-for="c in commits">
        <div class="card" :id="c.revision_hash">
          <div class="card-header">
            <div v-on:click="scrollToCommit(c)">
              <i class="fa fa-bug"></i> Commit <a :href="vcs_url + c.revision_hash" target="_blank">{{c.revision_hash}}</a>
              <button class="btn btn-primary" v-on:click="top()" style="float: right;">Jump to top</button>
            </div>
          </div>
          <div :id="'collapse' + c.revision_hash">
            <div class="card-block">
              <div class="row">
                <label class="col-sm-2">Commit Message</label>
                <div class="col-sm-10">
                  <pre class="form-control">{{ c.message }}</pre>
                </div>
              </div>
            </div>
            <div>
              <template v-for="f in c.changes">
                <TechnologyMonacoDiffView :commit="c" :file="f" :lines="f.lines" :existingTechnologies="technologies" ref="diffView" />
              </template>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { alert } from 'vue-strap'
import rest from '../api/rest'
import TechnologyMonacoDiffView from '@/components/TechnologyMonacoDiffView.vue'
import Multiselect from 'vue-multiselect'

export default {
    data() {
      return {
        commits: [],
        issue: '',
        flashes: [],
        error: [],
        vcs_url: '',
        issue_url: '',
        technologies: []
      }
    },
    computed: mapGetters({
      currentProject: 'currentProject',
      projectsVcs: 'projectsVcs',
      projectsIts: 'projectsIts',
      projectsMl: 'projectsMl'
    }),
    mounted() {

        this.$store.dispatch('pushLoading')
        rest.getTechnologiesForTechnologyLabeling(this.currentProject.name)
            .then(response => {
                this.$store.dispatch('popLoading')
                this.technologies = response.data['technologies']
            })
            .catch(e => {
                this.$store.dispatch('pushError', e)
            });

        var that = this;

        // Start background request
        this.$store.dispatch('pushLoading')
        rest.sampleCommitForTechnologyLabeling(this.currentProject.name)
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
                this.has_trained = response.data['has_trained']
                this.load_last = response.data['load_last']
                setTimeout(() => {
                    // Register all editors
                    this.registerFoldingModel();
                    this.initEditors();
                    this.validateAll();
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
        TechnologyMonacoDiffView,
        alert,
        Multiselect
    },
    methods: {
        top : function() {
            scroll(0,0)
        },
        initEditors: function() {     
            for(var i = 0; i < this.$refs.diffView.length; i++)
            {
                this.$refs.diffView[i].initEditor();
            }
        },
        getEditors : function() {
            var editors = [];
            for(var i = 0; i < this.$refs.diffView.length; i++)
            {
                editors.push(this.$refs.diffView[i].getEditor());
            }
            return editors;
        },
        validate: function() {
            var correct = [];
            for(var i = 0; i < this.$refs.diffView.length; i++)
            {
                if(!this.$refs.diffView[i].validateEditor())
                {
                    correct.push(this.commit.changes[i]);
                }
            }
            return correct;
        },
        showValidation: function(show) {
            for(var i = 0; i < this.$refs.diffView.length; i++)
            {
                this.$refs.diffView[i].changeValidation(show);
            }
        },
        getData: function() {
            var data = {};
            var hash = this.commit.revision_hash;
            for(var i = 0; i < this.$refs.diffView.length; i++)
            {
                data = Object.assign({}, data, this.$refs.diffView[i].getData(hash));
            }
            return data;
        },

        jumpToChange : function(change)
        {
            document.getElementById('file' + change.filename + change.parent_revision_hash).scrollIntoView();
        },
        getEditors : function() {
           var editors = [];
           for(var i = 0; i < this.$refs.diffView.length; i++)
           {
           editors = editors.concat(this.$refs.diffView[i].getEditors());
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
                    for (var i = 0; i < that.$refs.diffView.length; i++) {
                        that.$refs.diffView[i].validateEditor()
                    }
             }, 1000);
        },
        submitLabels : function() {
             // check if anything is missing
             var correct = [];
             for (var i = 0; i < this.$refs.diffView.length; i++) {
                  correct = correct.concat(this.$refs.diffView[i].validateEditor());
                  this.$refs.diffView[i].changeValidation(true);
             }
             this.error = correct;
             console.log(this.error);
             if(correct.length > 0) {
                window.alert("Not all lines are labelled. You can find links to the locations you missed at the top of the page and the files.");
                return;
             }
             // else collect data for transmit
             var data = {};
             for (var i = 0; i < this.$refs.diffView.length; i++) {
                 data = Object.assign({}, data, this.$refs.diffView[i].getData());
             }

            console.log(data);
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
