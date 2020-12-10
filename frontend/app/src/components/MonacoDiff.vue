<template>
<div>
  <div class="card-header" ref="header" :id="'file' + file.filename + file.parent_revision_hash">
    <div style="margin-bottom: 5px;">{{ file.filename }}</div>
    <div>
      <div class="label">
        <slot name="labels"></slot>
      </div>
      <button class="btn btn-primary" v-on:click="next()" style="float: right;">Next ></button>
      <button class="btn btn-primary" v-on:click="back()" style="float: right;">< Previous</button>
      <button class="btn btn-primary" v-on:click="top()" style="float: right;">Jump to top</button>
    </div>
    <div>
      <div v-if="missingChanges.length > 0">
        <ul>
           <li v-for="item in missingChanges">
              Original: {{ item.originalStartLineNumber }} - {{ item.originalEndLineNumber }} / Modified: {{ item.modifiedStartLineNumber }} - {{ item.modifiedEndLineNumber }}
              <button class="btn btn-primary btn-xs" v-on:click="jumpToChange(item)">Jump to</button>
          </li>
        </ul>
      </div>
    </div>
  </div>
  <div class="card-block" style="padding: 0px">
    <MonacoEditor class="editor" :diffEditor="true" :value="file.after" :original="file.before" :options="options" :language="editorLanguage" ref="editor" @editorWillMount="editorWillMount" @editorDidMount="editorDidMount"/>
  </div>
</div>
</template>

<script>
import MonacoEditor from 'vue-monaco'

export default {
  data() {
    return {
      decorationsLeft: [],
      decorationsObjectsLeft: {},
      decorationsRight: [],
      decorationsObjectsRight: {},
      metaLeft: {},
      metaRight: {},

      originalLinesNeeded: {},
      modifiedLinesNeeded: {},
      missingChanges: [],
      options: {glyphMargin: true, readOnly: true, ignoreTrimWhitespace: false}
    }
  },
  props: {
      file : Object,
      commit: Object,
      labels: Array
  },
  components: {
      MonacoEditor
  },
  computed: {
    // this is used for syntax highlighting
    editorLanguage: function () {
      if(this.file.filename.endsWith('.java')) {
        return "java"
      }else if(this.file.filename.endsWith('.xml')) {
        return "xml"
      }else {
        return ""
      }
    }
  },
  methods: {
    // todo: we should switch most of these functions to emit events to the parent
    // so that we can focus on displaying the file in this view while collecting the data in the parent
    //
    // todo: this is a crutch to allow acces from outside to our MonacoEditor instance
    getEditor: function() {
      return this.$refs.editor.getEditor();
    },
    // todo: second crutch to allow checking from outside if this is a modified lineh
    isModified: function(lineNumber, isOriginal) {
      return (isOriginal && typeof this.originalLinesNeeded[lineNumber] !== 'undefined') || (!isOriginal && typeof this.modifiedLinesNeeded[lineNumber] !== 'undefined')
    },
    // todo: third crutch to get data from parent
    getData: function() {
      let data = {}
      data[this.commit.revision_hash + "_" + this.file.parent_revision_hash + "_" + this.file.filename] = {}
      for(let line in this.decorationsObjectsLeft) {
        let label = this.decorationsObjectsLeft[line].options.linesDecorationsClassName
        let mappedLine = line
        for(let ml of this.file.lines) {
            if(ml['new'] == '-' && ml['old'] == line) {
              mappedLine = ml['number']
            }
         }
        data[this.commit.revision_hash + "_" + this.file.parent_revision_hash + "_" + this.file.filename][mappedLine] = label
      }
      for(let line in this.decorationsObjectsRight) {
        let label = this.decorationsObjectsRight[line].options.linesDecorationsClassName
        let mappedLine = line
        for(let ml of this.file.lines) {
            if(ml['old'] == '-' && ml['new'] == line) {
              mappedLine = ml['number']
            }
         }
        data[this.commit.revision_hash  + "_" + this.file.parent_revision_hash + "_" + this.file.filename][mappedLine] = label
      }
      return data
    },
    getMeta: function(lineNumber, isOriginal) {
      if(isOriginal && typeof this.metaLeft[lineNumber] !== 'undefined') {
        return this.metaLeft[lineNumber]
      }
      if(!isOriginal && typeof this.metaRight[lineNumber] !== 'undefined') {
        return this.metaRight[lineNumber]
      }
    },
    editorWillMount(monaco) {
      this.$emit('editorWillMount', monaco)
    },
    initLines(editor) {
      // todo: these should come from parent!
      const labelCssClass = this.labels

      for(let line of this.file.lines) {
        if(line['new'] == '-') {
          this.originalLinesNeeded[line['old']] = line['number']
          if(line.label > 0) {
            this.setLabelLeft(line['old'], labelCssClass[line.label - 1])
          }
          if(line.meta_data !== null) {
            this.setPreLabelLeft(line['old'], 'bugfix')
            this.metaLeft[line['old']] = line['meta_data']
          }
        }
        if(line['old'] == '-') {
          this.modifiedLinesNeeded[line['new']] = line['number']
          if(line.label > 0) {
            this.setLabelRight(line['new'], labelCssClass[line.label - 1])
          }
          if(line.meta_data !== null) {
            this.setPreLabelRight(line['new'], 'bugfix')
            this.metaRight[line['new']] = line['meta_data']
          }
        }
      }
    },
    setPreLabelLeft: function(line, label) {
      if(line in this.decorationsObjectsLeft) {
        this.decorationsObjectsLeft[line].options.glyphMarginClassName = label
      }else {
        this.decorationsObjectsLeft[line] = {
          range: new monaco.Range(line, 1, line, 1),
          options: {
              isWholeLine: true,
              glyphMarginClassName: label
          }
        }
      }
    },
    setPreLabelRight: function(line, label) {
      if(line in this.decorationsObjectsRight) {
        this.decorationsObjectsRight[line].options.glyphMarginClassName = label
      }else {
        this.decorationsObjectsRight[line] = {
          range: new monaco.Range(line, 1, line, 1),
          options: {
              isWholeLine: true,
              glyphMarginClassName: label
          }
        }
      }
    },
    setLabelLeft: function(line, label) {
      if(line in this.decorationsObjectsLeft) {
        this.decorationsObjectsLeft[line].options.linesDecorationsClassName = label
      }else {
        this.decorationsObjectsLeft[line] = {
          range: new monaco.Range(line, 1, line, 1),
          options: {
              isWholeLine: true,
              linesDecorationsClassName: label
          }
        }
      }
    },
    setLabelRight: function(line, label) {
      if(line in this.decorationsObjectsRight) {
        this.decorationsObjectsRight[line].options.linesDecorationsClassName = label
      }else {
        this.decorationsObjectsRight[line] = {
          range: new monaco.Range(line, 1, line, 1),
          options: {
              isWholeLine: true,
              linesDecorationsClassName: label
          }
        }
      }
    },
    lateInit: function(editor) {
      // set pre-labels, initialize lines
      this.initLines(editor)

      // add jump actions for changes
      this.addJumpActions(editor)

      // add label actions
      this.addLabelActions(editor)

      // overwrite editor diff decorations with our own
      editor._diffComputationResult = {changes: this.calculateLineChanges(this.file.hunks)}
      editor._beginUpdateDecorations = function() {
        // console.log('i should update');
      }

      let left = editor.getOriginalEditor()
      let right = editor.getModifiedEditor()
      this.decorationsLeft = left.deltaDecorations(this.decorationsLeft, Object.values(this.decorationsObjectsLeft))
      this.decorationsRight = right.deltaDecorations(this.decorationsRight, Object.values(this.decorationsObjectsRight))
    },
    editorDidMount(editor) {
      this.$emit('editorDidMount', editor)

      // this is a crutch to shove the data into the editor because monaco has no finishedLoading event
      const didScrollChangeDisposable = editor.getModifiedEditor().onDidScrollChange((event) => {
          didScrollChangeDisposable.dispose();
          
          console.log('editor initialized');

          this.lateInit(editor)
      });

    },
    runBack(ed, editor) {
      let isOriginal = editor.getEditor().getOriginalEditor() == ed
      let currentLine = ed.getPosition().lineNumber

      // find previous change
      let previousChangeLine
      if(isOriginal) {
        for(let i = currentLine; i > 0; i--) {
          if(typeof this.originalLinesNeeded[i] !== 'undefined') {
            previousChangeLine = i 
            break
          }
        }
      }else {
        for(let i = currentLine; i > 0; i--) {
          if(typeof this.modifiedLinesNeeded[i] !== 'undefined') {
            previousChangeLine = i 
            break
          }
        }
      }

      if(typeof previousChangeLine !== 'undefined') {
        ed.revealLineInCenter(previousChangeLine)
        ed.setPosition({column: 1, lineNumber: previousChangeLine})
      }
    },
    runNext(ed, editor) {
      let isOriginal = editor.getEditor().getOriginalEditor() == ed
      let currentLine = ed.getPosition().lineNumber

      let nextChangeLine
      if(isOriginal) {
        for(let line in this.originalLinesNeeded) {
          if(line > currentLine) {
            nextChangeLine = line
            break
          }
        }
      }else {
        for(let line in this.modifiedLinesNeeded) {
          if(line > currentLine) {
            nextChangeLine = line
            break
          }
        }
      }

      if(typeof nextChangeLine !== 'undefined') {
        ed.revealLineInCenter(nextChangeLine)
        ed.setPosition({column: 1, lineNumber: nextChangeLine})
      }
    },
    calculateLineChanges: function(hunks) {
      let changes = []
      for(let hunk of hunks) {

        var originalStartLineNumber;
        var originalEndLineNumber;
        var modifiedStartLineNumber;
        var modifiedEndLineNumber;
        if (hunk.originalLength === 0) {
          originalStartLineNumber = hunk.originalStart;
          originalEndLineNumber = 0;
        }else {
          originalStartLineNumber = hunk.originalStart + 1;
          originalEndLineNumber = hunk.originalStart + hunk.originalLength;
        }
        if (hunk.modifiedLength === 0) {
            modifiedStartLineNumber = hunk.modifiedStart;
            modifiedEndLineNumber = 0;
        }
        else {
            modifiedStartLineNumber = hunk.modifiedStart + 1;
            modifiedEndLineNumber = hunk.modifiedStart + hunk.modifiedLength;
        }

        changes.push({originalStartLineNumber: originalStartLineNumber, originalEndLineNumber: originalEndLineNumber, modifiedStartLineNumber: modifiedStartLineNumber, modifiedEndLineNumber: modifiedEndLineNumber})
      }
      return changes
    },
    addJumpActions: function(editor)  {
      let prev = {
          id: 'backQ',
          label: "Jump to previous diff",
          keybindings: [ monaco.KeyCode.KEY_Q ],
          precondition: null,
          keybindingContext: null,
          contextMenuGroupId: 'navigation',
          contextMenuOrder: '21',
          run: (ed) => {
             this.runBack(ed, editor);
          }
      }
      let next = {
          id: 'nextW',
          label: "Jump to next diff",
          keybindings: [ monaco.KeyCode.KEY_W ],
          precondition: null,
          keybindingContext: null,
          contextMenuGroupId: 'navigation',
          contextMenuOrder: '22',
          run: (ed) => {
             this.runNext(ed, editor);6
          }
      }
      editor.getOriginalEditor().addAction(prev)
      editor.getOriginalEditor().addAction(next)
      editor.getModifiedEditor().addAction(prev)
      editor.getModifiedEditor().addAction(next)
    },
    top: function() {
      scroll(0,0)
    },
    // todo: these only jump to original
    back: function() {
      this.runBack(this.$refs.editor.getEditor().getOriginalEditor(), this.$refs.editor);
    },
    next: function() {
      this.runNext(this.$refs.editor.getEditor().getOriginalEditor(), this.$refs.editor);
    },
    jumpToChange: function(change) {
      let ed = this.$refs.editor.getEditor().getOriginalEditor();
      ed.revealLineInCenter(change.originalStartLineNumber);
      ed.setPosition({column: 1, lineNumber: change.originalStartLineNumber});
    },
    // todo: this should be passed from outside
    addLabelActions: function(editor) {
      this.addLabelAction(editor, '1', 'PMD warning', [ monaco.KeyCode.KEY_1 ], 'bugfix')
      this.addLabelAction(editor, '2', 'Remove label', [ monaco.KeyCode.KEY_2 ], '')
      /*      
      let i = 0
      for(let label of this.labels) {
        i++
        keycode = monaco.KeyCode['Key_' + i]
        this.addLabelAction(editor, i.toString(), label, [ keycode ], label)
      }
      i++
      this.addLabelAction(editor, i.toString(), 'Remove label', [ keycode ], '')
      */

     /*     
     this.addLabelAction(editor, '1', 'Bugfix', [ monaco.KeyCode.KEY_1 ], 'bugfix');
     this.addLabelAction(editor, '2', 'Whitespace', [ monaco.KeyCode.KEY_2 ], 'whitespace');
     this.addLabelAction(editor, '3', 'Documentation', [ monaco.KeyCode.KEY_3 ], 'documentation');
     this.addLabelAction(editor, '4', 'Refactoring', [ monaco.KeyCode.KEY_4 ], 'refactoring');
     this.addLabelAction(editor, '5', 'Test', [ monaco.KeyCode.KEY_5 ], 'test');
     this.addLabelAction(editor, '6', 'Unrelated', [ monaco.KeyCode.KEY_6 ], 'unrelated');
     this.addLabelAction(editor, '7', 'Remove label', [ monaco.KeyCode.KEY_7 ], '');*/
    },
    labelAction: function(ed, label) {
      const range = ed.getSelection()
      const isOriginal = ed === this.$refs.editor.getEditor().getOriginalEditor()

      let left = false
      let right = false
      for(let lineNumber = range.startLineNumber; lineNumber <= range.endLineNumber; lineNumber++) {
        if(isOriginal && typeof this.originalLinesNeeded[lineNumber] !== 'undefined') {
          this.setLabelLeft(lineNumber, label)
          left = true
        }else if(!isOriginal && typeof this.modifiedLinesNeeded[lineNumber] !== 'undefined') {
          this.setLabelRight(lineNumber, label)
          right = true
        }
      }

      if(left === true) {
        this.decorationsLeft = ed.deltaDecorations(this.decorationsLeft, Object.values(this.decorationsObjectsLeft))
      }
      if(right === true) {
        this.decorationsRight = ed.deltaDecorations(this.decorationsRight, Object.values(this.decorationsObjectsRight))
      }
    },
    addLabelAction: function(editor, id, label, keybindings, labelName) {
      let labelAction = {
          id: id,
          label: label,
          keybindings: keybindings,
          precondition: null,
          keybindingContext: null,
          contextMenuGroupId: 'navigation',
          contextMenuOrder: id,
          run: (ed) => {
            this.labelAction(ed, labelName)
            return null
          }
      }
      editor.getOriginalEditor().addAction(labelAction)
      editor.getModifiedEditor().addAction(labelAction)
    }
  }
}
</script>