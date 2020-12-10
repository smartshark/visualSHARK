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
         <i class="fa fa-bug"></i> <a :href="issue_url + issue.external_id" target="_blank">{{issue.external_id}}</a> - {{issue.title}}
        </div>
        <div class="card-block">
          <div class="row">
            <label class="col-sm-2">Issue title</label>
            <div class="col-sm-10">{{ issue.title }}</div>
          </div>
          <div class="row">
            <label class="col-sm-2">Issue description</label>
            <div class="col-sm-10">
<pre class="force-wrap">{{ issue.desc }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
      <template v-for="c in commits">
        <div class="card" :id="c.revision_hash">
          <div class="card-header">
            <div>
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
                <MonacoDiff :commit="c" :file="f" :labels="labels" ref="diffView" @editorWillMount="editorWillMount" @editorDidMount="editorDidMount">
                  <template v-slot:labels>
                    <div class="label"><span class="dot" style="background-color: #FF0000;">1</span>PMD Warnings</div>
                    <div class="label"><span class="dot" style="background-color: grey">2</span>Remove label</div>
                  </template>
                </MonacoDiff>
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
import MonacoDiff from '@/components/MonacoDiff.vue'
import Multiselect from 'vue-multiselect'

export default {
  data() {
    return {
      commits: [],
      issue: '',
      flashes: [],
      error: [],
      pmd_warnings: [],
      vcs_url: '',
      issue_url: '',
      labels: ['bugfix', 'whitespace','documentation', 'refactoring', 'test', 'unrelated'],
      didMount: false
    }
  },
  mounted() {
    this.$store.dispatch('pushLoading')
    rest.sampleIssueFromPMD()
      .then(response => {
        this.$store.dispatch('popLoading')
        this.commits = response.data['commits'];
        this.issue = response.data['issue'];
        this.vcs_url = response.data['vcs_url']
        this.issue_url = response.data['issue_url']
      })
      .catch(e => {
        this.$store.dispatch('pushError', e)
        this.$store.dispatch('popLoading')
    })
  },
  components: {
    MonacoDiff,
    alert,
    Multiselect
  },
  methods: {
    editorDidMount: function(editor) {
    },
    editorWillMount: function(monaco) {
      if(!this.didMount) {
        monaco.languages.registerHoverProvider('java', {
          provideHover: (model, position) => {
            // let isOriginal = model == this.$refs.editor.getEditor().getOriginalEditor().getModel()
            // check if we hover over a line with a label
            for(let i = 0; i < this.$refs.diffView.length; i++) {
              let m = this.$refs.diffView[i]

              // problematic:
              // the information has to come from the editor as in this way we would have to distinguish between files!
              let contents = []
              contents.push({value: '***PMD warnings***'})
              if(m.getEditor().getModel().original == model && typeof m.getMeta(position.lineNumber, true) !== 'undefined') {
                for(let warning of m.getMeta(position.lineNumber, true)) {
                  contents.push({value: warning})
                }
              }

              if(m.getEditor().getModel().modified == model && typeof m.getMeta(position.lineNumber, false) !== 'undefined') {
                for(let warning of m.getMeta(position.lineNumber, false)) {
                  contents.push({value: warning})
                }
              }
              
              if(contents.length > 1) {
                return {
                  contents: contents
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
    jumpToChange: function(change) {
      document.getElementById('file' + change.filename + change.parent_revision_hash).scrollIntoView();
    },
    submitLabels: function() {
      let data = {}
      for (let i = 0; i < this.$refs.diffView.length; i++) {
        data = Object.assign({}, data, this.$refs.diffView[i].getData());
      }
      this.$store.dispatch('pushLoading')
      let result = {labels : data, issue_id: this.issue.id}
      rest.savePMDLabels({ data : result})
      .then(response => {
          this.$store.dispatch('popLoading');
      })
      .catch(e => {
          this.$store.dispatch('pushError', e)
      })
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
