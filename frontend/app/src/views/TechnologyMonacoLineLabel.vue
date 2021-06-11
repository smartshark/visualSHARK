<template>
  <div class="wrapper">
    <template v-if="flashes">
      <b-alert v-for="flash in flashes" :key="flash.id" placement="top-center" duration="5" variant="success" dismissable>
        <span class="icon-info-circled alert-icon-float-left"></span>
        <p>{{flash.message}}</p>
      </b-alert>
    </template>
    <div class="animated fadeIn">
      <div v-if="error.length > 0">
        <b-alert placement="top-center" duration="5" variant="warning">
          <ul>
            <li v-for="item in error" :key="item.parent_revision_hash+item.filename">
              Missing labels in commit {{ item.parent_revision_hash }}, file {{ item.filename }}
              <button class="btn btn-primary btn-xs" v-on:click="jumpToChange(item)">Jump to</button>
            </li>
          </ul>
        </b-alert>
      </div>
      <button class="btn btn-primary" v-on:click="submitLabels()" style="float: right; margin-bottom: 5px;">Submit labels</button>
      <button v-if="loadId" class="btn btn-primary" v-on:click="loadNext()" style="float: right; margin-bottom: 5px; margin-right: 5px;">Load next</button>
      <div class="clearfix"></div>
        <div class="card">
        <div class="card-header">
          <i class="fa fa-question"></i> Instructions
        </div>
        <div class="card-block">
          <ul>
            <li>Select changed code to label</li>
            <li>Press 1 or 2 on keyboard, 1 starts a line-wise label, 2 starts block-wise label</li>
            <li>Use dropdown to select technologies or add new ones</li>
            <li>Press set button</li>
            <li>To remove a label follow the same procedure without selecting a technology</li>
            <li>To see technologies that are labeled hover over the line of the code</li>
          </ul>
        </div>
      </div>
      <div class="card">
        <div class="card-header">
          <i class="fa fa-tag"></i> Most used technologies
        </div>
        <div class="card-block">
          TAG CLOUD: <template v-for="(number, tech) in counts">{{tech}}({{number}})&nbsp;</template>
        </div>
      </div>
      <template v-for="c in commits">
        <div class="card" :id="c.revision_hash" :key="c.revision_hash">
          <div class="card-header">
            <div v-on:click="scrollToCommit(c)">
              <i class="fa fa-code"></i> Commit <a :href="vcs_url + c.revision_hash" target="_blank">{{c.revision_hash}}</a>
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
                <TechnologyMonacoDiffView :key="c.revision_hash + f.filename" :commit="c" :file="f" :lines="f.lines" :existingTechnologies="technologies" :readOnly="true" ref="diffView" @editorWillMount="editorWillMount" @addTechnology="addTechnology"/>
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
import rest from '../api/rest'
import TechnologyMonacoDiffView from '@/components/TechnologyMonacoDiffView.vue'

export default {
    data() {
      return {
        commits: [],
        issue: '',
        flashes: [],
        error: [],
        vcs_url: '',
        issue_url: '',
        technologies: [],
        counts: [],
        didMount: false
      }
    },
    props: {
      loadId: String
    },
    computed: mapGetters({
      currentProject: 'currentProject',
      projectsVcs: 'projectsVcs',
      projectsIts: 'projectsIts',
      projectsMl: 'projectsMl'
    }),
    mounted() {
        let req = {project: this.currentProject.name, id: null}
        if(typeof this.loadId !== 'undefined') {
          req.id = this.loadId
        }
        this.$store.dispatch('pushLoading')
        rest.getTechnologiesForTechnologyLabeling()
          .then(response => {
            this.$store.dispatch('popLoading')
            this.technologies = response.data['technologies']
            this.counts = response.data['counts']
          })
          .catch(e => {
            this.$store.dispatch('pushError', e)
          });

        //var that = this;

        // Start background request
        this.$store.dispatch('pushLoading')
        rest.sampleCommitForTechnologyLabeling(req)
            .then(response => {
                this.$store.dispatch('popLoading')

                console.log(response.data)

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
                    //this.registerFoldingModel();
                    this.initEditors();
                    this.validateAll();
                }, 25);

/*                if(this.has_trained !== true) {
                    this.flashes.push({id: 'train', message: 'You have not finished the training! Loading training issues first!'})
                }
*/
                if(this.load_last === true) {
                     this.flashes.push({id: 'last', message: 'You have not finished labeling the last issue, loading last issue first.'})
                }
            })
            .catch(e => {
                this.$store.dispatch('pushError', e)
            });
    },
    components: {
        TechnologyMonacoDiffView
    },
    methods: {
        addTechnology: function(tech) {
          if(!this.technologies.includes(tech)) {
            this.technologies.push(tech)
          }
        },
        loadNext: function() {
          this.$router.push('/labeling/technology/')
          setTimeout(() => {
            window.location.reload(false);
          }, 25)
        },
        editorWillMount: function(monaco) {
          if(!this.didMount) {
            monaco.languages.registerHoverProvider('csharp', {
              provideHover: (model, position) => {
                // let isOriginal = model == this.$refs.editor.getEditor().getOriginalEditor().getModel()
                // check if we hover over a line with a label
                for(let i = 0; i < this.$refs.diffView.length; i++) {
                    let m = this.$refs.diffView[i].getEditor()
                    let isOriginal = m.getEditor().getModel().original == model

                    if(m.getEditor().getModel().original == model || m.getEditor().getModel().modified == model) {
                      
                      // todo: there ought to be a better way than hhis, maybe use lines?
                      if(this.$refs.diffView[i].isModified(position.lineNumber, isOriginal)) {
                        //console.log('line number', position.lineNumber, 'in', this.$refs.diffView[i].file.filename, 'original', isOriginal)
                        let techs = this.$refs.diffView[i].getTechnologiesForLine(position.lineNumber, isOriginal)
                        console.log(techs)
                        return {
                          //range: new monaco.Range(1, 1, model.getLineCount(), model.getLineMaxColumn(model.getLineCount())),
                          contents: [
                            { value: '**Technologies**' },
                            { value:  techs['techs']},
                            { value:  techs['type']}
                          ]
                        }

                      }
                    }
                }
              }
            })
            this.didMount = true 
          }
        },
        top: function() {
            scroll(0,0)
        },
        initEditors: function() {     
            for(var i = 0; i < this.$refs.diffView.length; i++)
            {
                this.$refs.diffView[i].initEditor();
            }
        },
        getEditors: function() {
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
            //var hash = this.commit.revision_hash;
            for(var i = 0; i < this.$refs.diffView.length; i++)
            {
                data = Object.assign({}, data, this.$refs.diffView[i].getData());
            }
            return data;
        },
        jumpToChange: function(change)
        {
            document.getElementById('file' + change.filename + change.parent_revision_hash).scrollIntoView();
        },
        validateAll: function () {
            var that = this;
            setTimeout(() => {
                    for (var i = 0; i < that.$refs.diffView.length; i++) {
                        that.$refs.diffView[i].validateEditor()
                    }
             }, 1000);
        },
        submitLabels: function() {
             // else collect data for transmit
             var labels = {};
             for (var i = 0; i < this.$refs.diffView.length; i++) {
                 labels = Object.assign({}, labels, this.$refs.diffView[i].getData());
             }

             var data = {revision_hash: this.commits[0].revision_hash, project_name: this.currentProject.name, labels: labels}
              this.$store.dispatch('pushLoading')
              rest.setCommitForTechnologyLabeling(data)
                .then(response => { // eslint-disable-line no-unused-vars
                  this.$store.dispatch('popLoading');
                  this.$router.push('/labeling/technology/')
                  setTimeout(() => {
                    window.location.reload(false);
                  }, 25)
                })
                .catch(e => {
                    this.$store.dispatch('pushError', e)
                    this.$store.dispatch('popLoading')
                });
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
.per-line {
    background: #FF0000;
    width: 5px !important;
    margin-left: 3px;
}
.per-block {
    background: #333333;
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
