<template>
  <div class="card diff-card">
    <div class="card-header" v-bind:class="{'complete': isComplete}">
      <i class="fa fa-file"></i> {{filename}}

      <!--Mark whole file as test <input type="checkbox" name="mark_test"/>
      Mark whole file as documentation <checkbox name="mark_documentation"/>-->


        <!--<button v-on:click="showCode = !showCode">Toggle Code</button>&nbsp;&nbsp;
        <button v-if="!isComplete" v-on:click="scrollToNext()">next change</button>-->


      <div class="card-actions2">
        <div class="switch-group">
          Show code
          <label class="w3c-switch">
            <input type="checkbox" v-model="showCode">
            <span class="w3c-slider"></span>
          </label>
        </div>
        <div class="dl-group">
          <button v-if="!isComplete" v-on:click="scrollToNext()" class="btn btn-secondary">next change</button>
        </div>
        <div class="dl-group">
        <dropdown class="inline" v-model="showDropdown">
          <span slot="button">
            label file as
          </span>
          <div slot="dropdown-menu" class="dropdown-menu dropdown-menu-right dl-dropdown">
              <div class="input-group">
                <input type="checkbox" v-model="isTest" class="checkbox-dropdown">
                <div class="checkbox-label">test</div>
              </div>
              <div class="input-group">
                <input type="checkbox" v-model="isDocumentation" class="checkbox-dropdown">
                <div class="checkbox-label">documentation</div>
              </div>
              <div class="input-group">
                <input type="checkbox" v-model="isUnrelated" class="checkbox-dropdown">
                <div class="checkbox-label">unrelated</div>
              </div>
          </div>
        </dropdown>
      </div>
      </div>
    </div>
    <transition name="flip">
    <div class="card-block" v-show="showCode">
      Change {{numberSelected}} to <select class="labelType" v-model="selected" @change="changeLinks()">
        <option name="label" value="label">label</option>
        <option name="test" value="test">test</option>
        <option name="whitespace" value="whitespace">whitespace</option>
        <option name="documentation" value="documentation">documentation</option>
        <option name="refactoring" value="refactoring">refactoring</option>
        <option name="unrelated" value="unrelated">unrelated</option>
        <option name="bug" value="bug">bug</option>
      </select>
      <div class="diffEditor">
        <div class="lineLabels noselect">
            <div class="lineno" v-for="line in lines">
            <template v-if="line.new == '-'">
              <input type="checkbox" v-model="selectedModels[line.number]" :name="'checkbox' + line.number" @change="selectOne($event)"/>
              <select :id="commit + '_' + filename + '_' + line.number" v-model="models[line.number]" class="labelType"  @change="changeLabel(line.number)">
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
              <input type="checkbox" v-model="selectedModels[line.number]" :name="'checkbox' + line.number" @change="selectOne($event)"/>
              <select :id="commit + '_' + filename + '_' + line.number" v-model="models[line.number]" class="labelType"  @change="changeLabel(line.number)">
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
        <div class="linesOld noselect">
          <div class="lineno" v-for="line in lines">
            {{line.old}}
          </div>
        </div>
        <div class="linesNew noselect">
          <div class="lineno" v-for="line in lines">
            {{line.new}}
          </div>
        </div>
        <pre class="code" v-html="markedBlock" @mouseup="setSelected"></pre>
      </div>
    </div>
    </transition>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { alert, dropdown } from 'vue-strap'
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
      plainText: '',
      selected: 'label',
      models: {},
      selectedModels: {},
      isComplete: false,
      isDocumentation: false,
      isTest: false,
      isUnrelated: false,
      showCode: true,
      showDropdown: false,
      numberSelected: 0
    }
  },
  components: {
    alert, dropdown
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
      this.showDropdown = false
    },
    isTest(oldValue, newValue) {
      if(this.isTest === true) {
        this.setAllModels('test')
      }
      if(this.isTest === false) {
        this.setAllModels('label')
      }
      this.showDropdown = false
    },
    isUnrelated(oldValue, newValue) {
      if(this.isUnrelated === true) {
        this.setAllModels('unrelated')
      }
      if(this.isUnrelated === false) {
        this.setAllModels('label')
      }
      this.showDropdown = false
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
          //console.log('page offsets', window.pageXOffset, window.pageYOffset)
          break
        }
      }
    },
    selectOne(event) {
      this.countSelected()
    },
    countSelected() {
      let tmp = 0
      for(let idx in this.selectedModels) {
        if(this.selectedModels[idx] === true) {
          tmp += 1
        }
      }
      this.numberSelected = tmp
    },
    setSelected() {
      let sel = window.getSelection();
      //console.log('sel nodes', sel.anchorNode, sel.focusNode)

      let ap = sel.anchorNode.parentNode.closest("span.line-number-line")
      let fp = sel.focusNode.parentNode.closest("span.line-number-line")
      if(ap === null || sel.anchorNode.parentNode.className == 'code') {
        ap = sel.anchorNode.previousElementSibling
      }
      if(fp === null|| sel.focusNode.parentNode.className == 'code') {
        fp = sel.focusNode.previousElementSibling
      }
      let start = parseInt(ap.dataset.line)
      let end = parseInt(fp.dataset.line)

      let tmp = start
      if(end > start) {
      }
      else if(end < start) {
        start = end
        end = tmp
      }else {
        return
      }

      sel.removeAllRanges()

      for(let m in this.selectedModels) {
        if(start <= parseInt(m) && parseInt(m) <= end) {
          this.selectedModels[m] = !this.selectedModels[m]
        }
      }
      
      this.countSelected()
    },
    initializeModel() {
      for(let line of this.lines) {
        // if new == - we are on a line only existing on old
        if(line.new == '-' || line.old == '-') {
          // see: https://vuejs.org/v2/guide/reactivity.html
          this.$set(this.models, line.number, 'label')
          this.$set(this.selectedModels, line.number, false)
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
          marked.push('<span data-line="' + line.number + '" class="line-number-line"><div class="removedCode">' + po.value + '</div></span>')
        }else if(line.old == '-') {
          marked.push('<span data-line="' + line.number + '" class="line-number-line"><div class="addedCode">' + po.value + '</div></span>')
        }else{
          marked.push('<span data-line="' + line.number + '" class="line-number-line">' + po.value + '</span>')
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
      let plain = []
      if(this.filename.toLowerCase().endsWith('.java')) {
        marked = this.loadSyntax('java')
      }else if(this.filename.toLowerCase().endsWith('.xml')) {
        marked = this.loadSyntax('xml')
      }else if(this.filename.toLowerCase().endsWith('.html')) {
        marked = this.loadSyntax('xml')
      }else {
        for(let line of this.lines) {
          if(line.new == '-') {
            marked.push('<span data-line="' + line.number + '" class="line-number-line"><div class="removedCode">' + line.code + '</div></span>')
          }else if(line.old == '-') {
            marked.push('<span data-line="' + line.number + '" class="line-number-line"><div class="addedCode">' + line.code + '</div></span>')
          }else{
            marked.push('<span data-line="' + line.number + '" class="line-number-line">' + line.code + '</span>')
          }
        }
      }
      for(let line of this.lines) {
        plain.push(line.code)
      }
      this.markedBlock = marked.join('\n')
      this.plainText = plain.join('\n')
    },
    changeLinks() {
      for(let idx in this.selectedModels) {
        if(this.selectedModels[idx] == true) {
          this.models[idx] = this.selected
          this.selectedModels[idx] = false
        }
      }
      this.selected = 'label'

      // check completeness
      this.checkComplete()
      this.countSelected()
    },
    changeLabel(modelIdx) {
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
    }
  }
}
</script>

<style>
@import '~highlight.js/styles/github-gist.css';

.noselect {
  user-select: none;
}

.diff-card {
  margin-bottom: 0rem;
  border-left-width: 0px;
  border-right-width: 0px;
  border-bottom-width: 0px;
}

.card-actions2 {
  position: absolute;
  top: 0;
  right: 0;
}

.btn-default {
  color: #263238;
  background-color: #fff;
  border-color: #b0bec5;
}

.btn-default:hover {
  color: #263238;
  background-color: #cecece;
  border-color: #b0bec5;
}


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
  width: 100%;
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
/* The switch - the box around the slider */
.w3c-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  margin-left: 5px;
}

/* Hide default HTML checkbox */
.w3c-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

/* The slider */
.w3c-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  -webkit-transition: .4s;
  transition: .4s;
}

.w3c-slider:before {
  position: absolute;
  content: "";
  height: 15px;
  width: 15px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  -webkit-transition: .4s;
  transition: .4s;
}

input:checked + .w3c-slider {
  background-color: #2196F3;
}

input:focus + .w3c-slider {
  box-shadow: 0 0 1px #2196F3;
}

input:checked + .w3c-slider:before {
  -webkit-transform: translateX(26px);
  -ms-transform: translateX(26px);
  transform: translateX(26px);
}

/* Rounded sliders */
.w3c-slider.round {
  border-radius: 30px;
}

.w3c-slider.round:before {
  border-radius: 50%;
}

.switch-group {
  float: left;
  height: 35px;
  margin-top: 5px;
  margin-bottom: 0px;
  background-color: white;
  margin-right: 5px;
  padding: 5px;
  padding-right: 8px;
  padding-top: 6px;
  border: 1px solid #ccc;
}

.dl-group {
  float: left;
  margin-top: 13px;
  margin-right: 5px;
}

.dl-dropdown {
  padding-left: 5px;
}
</style>
