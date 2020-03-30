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
          <div class="lineno" v-for="(lineno, key, index) in lines">
            <select :id="commit + '_' + filename + '_' + lineno.old" v-model="models[lineno.old]" v-if="lineno.new == '-'" class="labelType" @change="changeLabel">
              <option name="label" value="label">label</option>
              <option name="whitespace" value="whitespace">whitespace</option>
              <option name="comment" value="comment">comment</option>
              <option name="refactoring" value="refactoring">refactoring</option>
              <option name="unrelated" value="unrelated">unrelated</option>
              <option name="bug" value="bug">bug</option>
            </select>
            <div class="lineno" v-if="lineno.new != '-'">{{index}}</div>
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
      proxLines: new Set()
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
          this.models[this.lines[lineno].old] = 'label'
        }
      }
    },
    refreshCode() {
      let tmp = this.code.join('')
      let i = 1
      let marked = []
      for(let line of hljs.highlight('java', tmp).value.split('\n')) {
        if(this.onlyDeleted.includes(i)) {
          marked.push('<span class="removedCode">- </span>' + line)
        }else if(this.onlyAdded.includes(i)) {
          marked.push('<span class="addedCode">+ </span>' + line)
        }else{
          marked.push(line)
        }
        i++
      }
      this.markedBlock = marked.join('\n')
    },
    changeLabel(event) {
      // check completeness
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

pre {
  font-size: 100%;
  overflow: auto;
  white-space: pre;
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
  background-color: rgba(255,0,0,0.2);
}

.addedCode {
  background-color: rgba(0,255,0,0.2);
}

.lineLabels {
  flex-shrink: 0;
  padding-top: 0px;
  margin-top: 0;
}
.linesNew {
  flex-shrink: 0;
  padding-top: 0px;
  margin-top: 0;
}
.linesOld {
  flex-shrink: 0;
  padding-top: 0px;
  margin-top: 0;
}
.labelType {
  -moz-appearance: none;
  -webkit-appearance: none;
  appearance: none;
  border: none;
}
</style>
