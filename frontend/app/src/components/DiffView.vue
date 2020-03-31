<template>
  <div class="card">
    <div class="card-header" v-bind:class="{'complete': isComplete}">
      <i class="fa fa-file"></i> {{filename}}
      <button v-on:click="showCode = !showCode">Toggle Code</button>
      <button v-if="!isComplete" v-on:click="scrollToNext()">next</button>
    </div>
    <div class="card-block" v-show="showCode">
      <div class="editor">
        <div class="lineLabels">
          <div class="lineno" v-for="(lineno, key, index) in lines" v-bind:class="{'selectedModel': selectedModels.includes(lineno.old)}" @click.left.shift.exact.prevent="selectModel(lineno.old, $event)">
            <select :id="commit + '_' + filename + '_' + lineno.old" v-model="models[lineno.old]" v-if="lineno.new == '-'" class="labelType"  @change="changeLabel(lineno.old)" @mousedown.left.shift.exact.prevent>
              <option name="label" value="label">label</option>
              <option name="whitespace" value="whitespace">whitespace</option>
              <option name="comment" value="comment">comment</option>
              <option name="refactoring" value="refactoring">refactoring</option>
              <option name="unrelated" value="unrelated">unrelated</option>
              <option name="bug" value="bug">bug</option>
            </select>
          </div>
        </div>
        <div class="linesOld">
          <div class="lineno" v-for="(lineno, key, index) in lines">
            {{lineno.old}}
          </div>
        </div>
        <div class="linesNew">
          <div class="lineno" v-for="(lineno, key, index) in lines">
            {{lineno.new}}
          </div>
        </div>
        <pre class="code" v-html="markedBlock"></pre>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { alert } from 'vue-strap'
import hljs from 'highlight.js/lib/highlight';
import java from 'highlight.js/lib/languages/java';

export default {
  props: {
    commit: String,
    filename: String,
    code: [Array, Object],
    lines: [Array, Object],
    onlyDeleted: [Array, Object],
    onlyAdded: [Array, Object]
  },
  data () {
    return {
      markedBlock: '',
      models: {},
      isComplete: false,
      showCode: true,
      margin: 2,
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
    this.refreshCode()
    this.refreshModel()

    // check if we are already finished because we only have additions
    if(this.onlyDeleted.length === 0) {
      this.isComplete = true
      this.showCode = false
    }
  },
  watch: {
    code: function(oldValue, newValue) {
      this.refreshCode()
    },
    lines: function(oldValue, newValue) {
      this.refreshModel()
    }
  },
  methods: {
    scrollToNext() {
      for(let el in this.models) {
        if(this.models[el] === 'label') {
          let k = this.commit + '_' + this.filename + '_' + el
          document.getElementById(k).scrollIntoView({behavior: 'smooth', block: 'nearest', inline: 'start' })
          break
        }
      }
    },
    refreshModel() {
      for(let lineno in this.lines) {
        if(this.lines[lineno].new == '-') {
          // see: https://vuejs.org/v2/guide/reactivity.html
          this.$set(this.models, this.lines[lineno].old, 'label')
          //this.models[this.lines[lineno].old] = 'label'
        }
      }
    },
    refreshCode() {
      // problem is that this maybe slow when compared to bulk operations
      // solution when syntax highlighting breaks
      // keep state https://github.com/highlightjs/highlight.js/issues/424
      // we could basically split by line and render each line while keeping the parser state
      let tmp = this.code.join('')
      let i = 1
      let marked = []

      let state = null
      for(let line of tmp.split('\n')) {
        let po = hljs.highlight('java', line, true, state)
        state = po.top
        if(this.onlyDeleted.includes(i)) {
          marked.push('<div class="removedCode">' + po.value + '</div>')
        }else if(this.onlyAdded.includes(i)) {
          marked.push('<div class="addedCode">' + po.value + '</div>')
        }else{
          marked.push(po.value)
        }
        i++
      }
      this.markedBlock = marked.join('\n')
    },
    changeLabel(modelIdx) {
      // check completeness
      let b = true
      for(let m in this.models) {
        if(this.models[m] == 'label') {
          b = false
        }
      }

      // check if we are linked, if we are change all linked labels
      if(this.selectedModels.includes(modelIdx)) {
        for(let m of this.selectedModels) {
          this.models[m] = this.models[modelIdx]
        }

        // reset linking
        this.selectedModels = []
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
.editor {
  width: 100%;
  height: 800px;
  display: flex;
  align-items: flex-start;
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
  line-height: 22px;
  margin-left: 10px;
}
.editor {
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}
.lineno {
  min-height: 22px;
  color: #aaa;
}
.lineLabels {
  flex-shrink: 0;
  padding-top: 0px;
  margin-top: 0;
  background-color: rgb(245, 242, 240);
}
.linesNew {
  flex-shrink: 0;
  padding-top: 0px;
  margin-top: 0;
  background-color: rgb(245, 242, 240);
}
.linesOld {
  flex-shrink: 0;
  padding-top: 0px;
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
}
</style>
