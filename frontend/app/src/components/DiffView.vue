<template>
  <div class="card">
    <div class="card-header" v-bind:class="{'complete': isComplete}">
      <i class="fa fa-file"></i> {{filename}}

      <!--Mark whole file as test <input type="checkbox" name="mark_test"/>
      Mark whole file as documentation <checkbox name="mark_documentation"/>-->
      <input type="checkbox" value="mark_test" v-model="isTest">
      Mark file as test
      <input type="checkbox" value="mark_documentation" v-model="isDocumentation">
      Mark file as documentation
      <button v-on:click="showCode = !showCode">Toggle Code</button>
      <button v-if="!isComplete" v-on:click="scrollToNext()">next</button>
    </div>
    <transition name="flip">
    <div class="card-block" v-show="showCode">
      <div class="diffEditor">
        <div class="lineLabels">
          <div class="lineno" v-for="line in lines" v-bind:class="{'selectedModel': selectedModels.includes(line.number)}" @click.left.shift.exact.prevent="selectModel(line.number, $event)">
            <template v-if="line.new == '-'">
              <select :id="commit + '_' + filename + '_' + line.number" v-model="models[line.number]" class="labelType"  @change="changeLabel(line.number)" @mousedown.left.shift.exact.prevent>
                <option name="label" value="label">label</option>
                <option name="test" value="test">test</option>
                <option name="whitespace" value="whitespace">whitespace</option>
                <option name="documentation" value="documentation">documentation</option>
                <option name="refactoring" value="refactoring">refactoring</option>
                <option name="unrelated" value="unrelated">unrelated</option>
                <option name="bug" value="bug">bug</option>
              </select>
            </template>
            <template v-if="line.old == '-'">
              <select :id="commit + '_' + filename + '_' + line.number" v-model="models[line.number]" class="labelType"  @change="changeLabel(line.number)" @mousedown.left.shift.exact.prevent>
                <option name="label" value="label">label</option>
                <option name="test" value="test">test</option>
                <option name="whitespace" value="whitespace">whitespace</option>
                <option name="documentation" value="documentation">documentation</option>
                <option name="refactoring" value="refactoring">refactoring</option>
                <option name="unrelated" value="unrelated">unrelated</option>
                <option name="bug" value="bug">bug</option>
              </select>
            </template>
          </div>
        </div>
        <div class="linesOld">
          <div class="lineno" v-for="line in lines">
            {{line.old}}
          </div>
        </div>
        <div class="linesNew">
          <div class="lineno" v-for="line in lines">
            {{line.new}}
          </div>
        </div>
        <pre class="code" v-html="markedBlock"></pre>
      </div>
    </div>
    </transition>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { alert } from 'vue-strap'
import hljs from 'highlight.js/lib/highlight';
import java from 'highlight.js/lib/languages/java';
import xml from 'highlight.js/lib/languages/xml';

export default {
  props: {
    commit: String,
    filename: String,
    parent: String,
    lines: Array
  },
  data () {
    return {
      markedBlock: '',
      models: {},
      isComplete: false,
      isDocumentation: false,
      isTest: false,
      showCode: true,
      selectedModels: []
    }
  },
  components: {
    alert
  },
  computed: mapGetters({
    currentProject: 'currentProject',
    projectsVcs: 'projectsVcs',
    projectsIts: 'projectsIts'
  }),
  created () {
    hljs.registerLanguage('java', java)
    hljs.registerLanguage('xml', xml)
    this.refreshCode()
    this.initializeModel()
  },
  watch: {
    lines: function(oldValue, newValue) {
      this.refreshCode()
      this.initializeModel()
    },
    isDocumentation(oldValue, newValue) {
      if(this.isDocumentation === true) {
        this.setAllModels('documentation')
      }
      if(this.isDocumentation === false) {
        this.setAllModels('label')
      }
    },
    isTest(oldValue, newValue) {
      if(this.isTest === true) {
        this.setAllModels('test')
      }
      if(this.isTest === false) {
        this.setAllModels('label')
      }
    }
  },
  methods: {
    setAllModels(label) {
      for(let el in this.models) {
        this.$set(this.models, el, label)
      }

      // change is not fired if we set it this way, we need to manually check completeness now
      this.checkComplete()

      if(this.isComplete !== true) {
        this.showCode = true
      }
    },
    scrollToNext() {
      for(let el in this.models) {
        if(this.models[el] === 'label') {
          let k = this.commit + '_' + this.filename + '_' + el
          document.getElementById(k).scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'})
          console.log('page offsets', window.pageXOffset, window.pageYOffset)
          break
        }
      }
    },
    initializeModel() {
      for(let line of this.lines) {
        // if new == - we are on a line only existing on old
        if(line.new == '-') {
          // see: https://vuejs.org/v2/guide/reactivity.html
          this.$set(this.models, line.number, 'label')
          //this.models[this.lines[lineno].old] = 'label'
        }
        if(line.old == '-') {
          this.$set(this.models, line.number, 'label')
        }
      }
    },
    loadSyntax(lang) {
      let marked = []
      let state = null
      for(let line of this.lines) {
        let po = hljs.highlight(lang, line.code, true, state)
        state = po.top
        if(line.new == '-') {
          marked.push('<div class="removedCode">' + po.value + '</div>')
        }else if(line.old == '-') {
          marked.push('<div class="addedCode">' + po.value + '</div>')
        }else{
          marked.push(po.value)
        }
      }
      return marked
    },
    refreshCode() {
      // todo:
      // - we can not use v-html for un-highlighted stuff, it breaks the html if the code contains <elements>
      // solution when syntax highlighting breaks
      // keep state https://github.com/highlightjs/highlight.js/issues/424
      let marked = []

      if(this.filename.toLowerCase().endsWith('.java')) {
        marked = this.loadSyntax('java')
      }else if(this.filename.toLowerCase().endsWith('.xml')) {
        marked = this.loadSyntax('xml')
      }else if(this.filename.toLowerCase().endsWith('.html')) {
        marked = this.loadSyntax('xml')
      }else {
        for(let line of this.lines) {
          if(line.new == '-') {
            marked.push('<div class="removedCode">' + line.code + '</div>')
          }else if(line.old == '-') {
            marked.push('<div class="addedCode">' + line.code + '</div>')
          }else{
            marked.push(line.code)
          }
        }
      }
      this.markedBlock = marked.join('\n')
    },
    changeLabel(modelIdx) {
      // check if we are linked, if we are changing all linked labels
      if(this.selectedModels.includes(modelIdx)) {
        for(let m of this.selectedModels) {
          this.models[m] = this.models[modelIdx]
        }

        // reset linking
        this.selectedModels = []
      }

      // check completeness
      this.checkComplete()
    },
    checkComplete() {
      let b = true
      for(let m in this.models) {
        if(this.models[m] == 'label') {
          b = false
        }
      }

      this.isComplete = b
      if(this.isComplete === true) {
        this.showCode = false
      }
    },
    selectModel(modelIdx, event) {
      if(typeof this.models[modelIdx] === 'undefined') {
        return
      }
      if(this.selectedModels.includes(modelIdx)) {
        this.selectedModels.splice(this.selectedModels.indexOf(modelIdx), 1)
      }else {
        this.selectedModels.push(modelIdx)
      }
    }
  }
}
</script>

<style>
@import '~highlight.js/styles/github-gist.css';

pre {
  font-size: 100%;
  overflow: auto;
  white-space: pre;
}
.selectedModel {
  border: 0px solid green;
  border-right-width: 1px;
}
.hideLine {
  display: none;
}
.complete {
  background-color: rgba(0,255,0,0.2);
}
.hideCode {
  display: none;
}
.showCode {
  display: block;
}
.diffEditor {
  width: 100%;
  height: 800px;
  display: flex;
  align-items: flex-start;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  overflow: auto;
  tab-size: 1.5em;
  -moz-tab-size: 1.5em;
}
.removedCode {
  display: inline;
  background-color: rgba(255,0,0,0.2);
}
.addedCode {
  display: inline;
  background-color: rgba(0,255,0,0.2);
}
.code {
  padding-top: 5px;
  line-height: 22px;
  margin-left: 10px;
  overflow: unset !important;
  white-space: pre !important;
}
.lineno {
  min-height: 22px;
  color: #aaa;
}
.lineLabels {
  flex-shrink: 0;
  padding-top: 5px;
  margin-top: 0;
  background-color: rgb(245, 242, 240);
  padding-left: 5px;
}
.linesNew {
  flex-shrink: 0;
  padding-top: 5px;
  padding-right: 5px;
  margin-top: 0;
  background-color: rgb(245, 242, 240);
}
.linesOld {
  flex-shrink: 0;
  padding-top: 5px;
  padding-right: 5px;
  margin-top: 0;
  background-color: rgb(245, 242, 240);
}
.labelType {
  -moz-appearance: none;
  -webkit-appearance: none;
  appearance: none;
  border: none;
  margin: 0px;
  padding: 0px;
  max-width: 50px;
  scroll-margin: 20px;
}
</style>
