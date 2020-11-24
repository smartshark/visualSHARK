<template>
<div>
  <div class="card-header" ref="header" :id="'file' + file.filename + file.parent_revision_hash">
    <div style="margin-bottom: 5px;">{{ file.filename }}</div>
    <div>
      <div class="label">
        Selected lines <template v-if="currentRange">{{currentRange}}</template><multiselect :id="'technologySelector' + file.filename + file.parent_revision_hash" v-model="selectedTechnologies" @tag="addTechnology" :taggable="true" :options="technologies" :multiple="true"></multiselect>
        <button v-if="currentRange.length > 0" v-on:click="setTechnologies()">Set</button>
      </div>

      <button class="btn btn-primary" v-on:click="next()" style="float: right;">Next ></button>
      <button class="btn btn-primary" v-on:click="back()" style="float: right;">< Previous</button>
      <button class="btn btn-primary" v-on:click="top()" style="float: right;">Jump to top</button>
    </div>
    <div>
      <div v-if="showValidation">
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
    <MonacoEditor class="editor" :diffEditor="true" :value="file.after" :original="file.before" :options="editorOptions" :language="editorLanguage" ref="editor" @editorWillMount="editorWillMount"/>
  </div>
</div>
</template>
<script>

import MonacoEditor from 'vue-monaco'
import Multiselect from 'vue-multiselect'


export default {
    data() {
      return {
        decorationsLeft: [],
        decorationsObjectsLeft: [],
        decorationsRight: [],
        decorationsObjectsRight: [],
        missingChanges: [],
        showValidation: false,
        selectedTechnologies: [],
        addedTechnologies: [],
        currentRange: [],
        selectedEditorType: null
      }
    },
    props: {
      file : Object,
      commit : Object,
      lines: Array,
      existingTechnologies: Array,
      readOnly: Boolean
    },
    components: {
      MonacoEditor,
      Multiselect
    },
    computed: {
      technologies: function () {
        return this.existingTechnologies.concat(this.addedTechnologies)
      },
      editorOptions: function () {
        return {readOnly: this.readOnly}
      },
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
        editorWillMount(monaco) {
          this.$emit('editorWillMount', monaco)
        },
        isModified(lineNumber, isOriginal) {
          return (isOriginal && this.getOriginalChangeForLine(lineNumber) !== null) || (!isOriginal && this.getModifiedChangeForLine(lineNumber) !== null)
        },
        getTechnologiesForLine(lineNumber, isOriginal) {
          let ret = 'none'
          if(isOriginal && typeof this.decorationsObjectsLeft[lineNumber] !== 'undefined') {
              ret = this.decorationsObjectsLeft[lineNumber].options.technologies
          }
          if(!isOriginal && typeof this.decorationsObjectsRight[lineNumber] !== 'undefined') {
              ret = this.decorationsObjectsRight[lineNumber].options.technologies
          }
          return ret
        },
        getOriginalChangeForLine(lineNumber) {
          let changes = this.$refs.editor.getEditor().getLineChanges()
          let returnHunk = null
          for(let hunk of changes) {
            if(hunk.originalStartLineNumber <= lineNumber && lineNumber <= hunk.originalEndLineNumber) {
              returnHunk = hunk
            }
          }
          return returnHunk
        },
        getModifiedChangeForLine(lineNumber) {
          let changes = this.$refs.editor.getEditor().getLineChanges()
          let returnHunk = null
          for(let hunk of changes) {
            if(hunk.modifiedStartLineNumber <= lineNumber && lineNumber <= hunk.modifiedEndLineNumber) {
              returnHunk = hunk
            }
          }
          return returnHunk
        },
        setTechnologies: function(click) {
          const isOriginal = this.selectedEditorType === this.$refs.editor.getEditor().getOriginalEditor()
          console.log('setting', this.selectedTechnologies, 'on', this.currentRange, 'on original?', isOriginal)
          if(isOriginal) {  
            for(let lineNumber of this.currentRange) {
              let hunk = this.getOriginalChangeForLine(lineNumber)
              this.decorationsObjectsLeft[lineNumber] = {
                range: new monaco.Range(lineNumber, 1, lineNumber, 1),
                options: {
                    isWholeLine: true,
                    linesDecorationsClassName: 'bugfix',  // this.selectedTechnologies.join()
                    technologies: this.selectedTechnologies.join()
                },
                change: hunk // this is the hunk, do we need it here?
              }
            }
            this.decorationsLeft = this.selectedEditorType.deltaDecorations(this.decorationsLeft, Object.values(this.decorationsObjectsLeft))
          }else {
            for(let lineNumber of this.currentRange) {
              let hunk = this.getModifiedChangeForLine(lineNumber)
              this.decorationsObjectsRight[lineNumber] = {
                range: new monaco.Range(lineNumber, 1, lineNumber, 1),
                options: {
                    isWholeLine: true,
                    linesDecorationsClassName: 'bugfix',  // this.selectedTechnologies.join()
                    technologies: this.selectedTechnologies.join()
                },
                change: hunk // this is the hunk, do we need it here?
              }
            }
            this.decorationsRight = this.selectedEditorType.deltaDecorations(this.decorationsRight, Object.values(this.decorationsObjectsRight))
          }

          this.validateEditor()

          this.selectedTechnologies = []
          this.currentRange = []
          this.selectedEditorType = null

          console.log(this.getData(this.commit.revision_hash))
        },
        addTechnology: function(newTechnology) {
          this.addedTechnologies.push(newTechnology)
          this.selectedTechnologies.push(newTechnology)
        },
        getEditor: function() {
            return this.$refs.editor;
        },
        initEditor: function() {
            var editor = this.$refs.editor;
            this.addActionToEditor(editor);
            this.jumpActions(editor);

            var labelCssClass = [ 'bugfix', 'whitespace','documentation', 'refactoring', 'test', 'unrelated'];
            for(var i = 0; i < this.file.lines.length; i++)
            {
              var line = this.file.lines[i];
              if(line.label > 0) {
                var label = labelCssClass[line.label-1];
                this.markLineInEditorLeft(line.old,label,this.$refs.editor,this.$refs.editor.getEditor().getOriginalEditor());
                this.markLineInEditorRight(line.new,label,this.$refs.editor,this.$refs.editor.getEditor().getModifiedEditor());
              }
            }
        },
        top : function() {
            scroll(0,0)
        },
        back : function() {
            this.runBack(this.$refs.editor.getEditor().getOriginalEditor(),this.$refs.editor);
        },
        next : function() {
            this.runNext(this.$refs.editor.getEditor().getOriginalEditor(),this.$refs.editor);
        },
        jumpToChange : function(change)
        {
         var ed = this.$refs.editor.getEditor().getOriginalEditor();
         ed.revealLineInCenter(change.originalStartLineNumber);
         ed.setPosition({column: 1, lineNumber: change.originalStartLineNumber});
        },
        changeValidation(show)
        {
          this.showValidation = show;
        },
        runBack(ed, editor) {
                   var currentLine = ed.getPosition().lineNumber;
                   console.log(currentLine);
                   var original = false;
                   if(editor.getEditor().getOriginalEditor() == ed)
                   {
                      original = true;
                   }
                   var changes = editor.getEditor().getLineChanges();
                   var foundChange = null;
                   for (var i = 0; i < changes.length; i++) {
                         var change = changes[i];
                         if((original && change.originalStartLineNumber < currentLine) || (!original && change.modifiedStartLineNumber < currentLine))
                         {
                                 foundChange = change;
                         }
                   }
                   if(foundChange != null)
                   {
                      if(original) {
                      ed.revealLineInCenter(foundChange.originalStartLineNumber);
                      ed.setPosition({column: 1, lineNumber: foundChange.originalStartLineNumber});
                      } else {
                      ed.revealLineInCenter(foundChange.modifiedStartLineNumber);
                      ed.setPosition({column: 1, lineNumber: foundChange.modifiedStartLineNumber});
                      }
                   }
        },
        runNext(ed, editor) {
             var currentLine = ed.getPosition().lineNumber;
                   console.log(currentLine)
                   var original = false;
                   if(editor.getEditor().getOriginalEditor() == ed)
                   {
                      original = true;
                   }
                   var changes = editor.getEditor().getLineChanges();
                   var foundChange = null;
                   for (var i = 0; i < changes.length; i++) {
                         var change = changes[i];
                         if((original && change.originalStartLineNumber > currentLine) || (!original && change.modifiedStartLineNumber > currentLine))
                         {
                                 foundChange = change;
                                 break;
                         }
                   }
                   if(foundChange != null)
                   {

                      if(original) {
                      ed.revealLineInCenter(foundChange.originalStartLineNumber);
                      ed.setPosition({column: 1, lineNumber: foundChange.originalStartLineNumber});
                      } else {
                      ed.revealLineInCenter(foundChange.modifiedStartLineNumber);
                      ed.setPosition({column: 1, lineNumber: foundChange.modifiedStartLineNumber});
                      }
                   }
        },
        jumpActions(editor) {
            var that = this;
            var action = {
                id: 'backQ',
                label: "Jump to previous diff",
                keybindings: [ monaco.KeyCode.KEY_Q ],
                precondition: null,
                keybindingContext: null,
                contextMenuGroupId: 'navigation',
                contextMenuOrder: '21',
                run: function(ed) {
                   that.runBack(ed,editor);
                }
            };
            editor.getEditor().getOriginalEditor().addAction(action);
            editor.getEditor().getModifiedEditor().addAction(action);

             var action2 = {
                id: 'nextW',
                label: "Jump to next diff",
                keybindings: [ monaco.KeyCode.KEY_W ],
                precondition: null,
                keybindingContext: null,
                contextMenuGroupId: 'navigation',
                contextMenuOrder: '22',
                run: function(ed) {
                   that.runNext(ed,editor);
                }
            };
            editor.getEditor().getOriginalEditor().addAction(action2);
            editor.getEditor().getModifiedEditor().addAction(action2);
        },
        labelTechnologyAction: function(editor, ed) {
          const range = ed.getSelection()
          const isOriginal = ed === this.$refs.editor.getEditor().getOriginalEditor()
          let lines = []

          for(let hunk of editor.getEditor().getLineChanges()) {
            for(let lineNumber = range.startLineNumber; lineNumber <= range.endLineNumber; lineNumber++) {

              // are changed lines part of the hunk lines?
              if(isOriginal) {
                if(hunk.originalStartLineNumber <= lineNumber && lineNumber <= hunk.originalEndLineNumber) {
                  lines.push(lineNumber)
                }
              }else {
                  if(hunk.modifiedStartLineNumber <= lineNumber && lineNumber <= hunk.modifiedEndLineNumber) {
                  lines.push(lineNumber)
                }
              }
            }
          }

          if(lines.length > 0) {
            this.currentRange = lines
            this.selectedEditorType = ed
            document.getElementById("technologySelector" + this.file.filename + this.file.parent_revision_hash).focus();
          }
          return null
        },
        addActionToEditor: function(editor) {
          this.addSingleActionToEditor2(editor, '1', 'Set technologies', [ monaco.KeyCode.KEY_1 ], this.labelTechnologyAction)
          this.addSingleActionToEditor(editor, '7', 'Remove technologies', [ monaco.KeyCode.KEY_7 ], '');
        },
        markLineInEditorLeft(lineNumber,className, editor,ed) {
                    var that = this;
                    var changes = editor.getEditor().getLineChanges();
                    var isInChange = false;
                    var foundChange;
                    for (var i = 0; i < changes.length; i++) {
                         var change = changes[i];
                         if((change.originalStartLineNumber <= lineNumber &&
                            lineNumber <= change.originalEndLineNumber))
                            {
                                 foundChange = change;
                                 isInChange = true;
                            }
                    }
                    if(isInChange) {
                      console.log('found change!', foundChange)
                    if(className == '') {
                      delete that.decorationsObjectsLeft[lineNumber];
                    } else {
                       that.decorationsObjectsLeft[lineNumber] = {
                        range: new monaco.Range(lineNumber, 1, lineNumber, 1),
                        options: {
                            isWholeLine: true,
                            linesDecorationsClassName: className
                        },
                        change: foundChange
                    };
                    }

                    that.decorationsLeft = ed.deltaDecorations(that.decorationsLeft, Object.values(that.decorationsObjectsLeft));
                        that.validateEditor();
                    }
        },
        markLineInEditorRight(lineNumber,className, editor,ed) {
                    var that = this;
                    var changes = editor.getEditor().getLineChanges();
                    var isInChange = false;
                    var foundChange;
                    for (var i = 0; i < changes.length; i++) {
                         var change = changes[i];
                         if(change.modifiedStartLineNumber <= lineNumber &&
                            lineNumber <= change.modifiedEndLineNumber)
                            {
                                 foundChange = change;
                                 isInChange = true;
                            }
                    }
                    if(isInChange) {
                    if(className == '') {
                      delete that.decorationsObjectsRight[lineNumber];
                    } else {
                    that.decorationsObjectsRight[lineNumber] = {
                        range: new monaco.Range(lineNumber, 1, lineNumber, 1),
                        options: {
                            isWholeLine: true,
                            linesDecorationsClassName: className
                        },
                        change: foundChange
                    };
                    }

                    that.decorationsRight = ed.deltaDecorations(that.decorationsRight, Object.values(that.decorationsObjectsRight));
                        that.validateEditor();
                    }
        },
        addSingleActionToEditor2: function(editor, id, label, keybindings, callback) {
          let actionLeft = {
            id: id,
            label: label,
            keybindings: keybindings,
            precondition: null,
            keybindingContext: null,
            contextMenuGroupId: 'navigation',
            contextMenuOrder: id,
            run: (ed) => {
              this.labelTechnologyAction(editor, ed)
              return null
            }
          };
          editor.getEditor().getOriginalEditor().addAction(actionLeft);
          editor.getEditor().getModifiedEditor().addAction(actionLeft);
        },
        addSingleActionToEditor: function(editor, id, label, keybindings, className) {
            var that = this;
            var actionLeft = {
                id: id,
                label: label,
                keybindings: keybindings,
                precondition: null,
                keybindingContext: null,
                contextMenuGroupId: 'navigation',
                contextMenuOrder: id,
                run: function(ed) {
                    var range = ed.getSelection();
                     for(var i = range.startLineNumber; i <= range.endLineNumber; i++)
                    {
                        that.markLineInEditorLeft(i,className,editor,ed);
                    }
                    return null;
                }
            };
            editor.getEditor().getOriginalEditor().addAction(actionLeft);

             var actionRight = {
                id: id,
                label: label,
                keybindings: keybindings,
                precondition: null,
                keybindingContext: null,
                contextMenuGroupId: 'navigation',
                contextMenuOrder: id,
                run: function(ed) {
                    var range = ed.getSelection();
                    for(var i = range.startLineNumber; i <= range.endLineNumber; i++)
                    {
                        that.markLineInEditorRight(i,className,editor,ed);
                    }
                    return null;
                }
            };
            editor.getEditor().getModifiedEditor().addAction(actionRight);
        },
        validateEditor: function() {
             var changes = this.$refs.editor.getEditor().getLineChanges();
             var isSomethingMissing = false;
             var lineDecorationsOrginal = this.decorationsObjectsLeft;
             var lineDecorationsModified = this.decorationsObjectsRight;
             this.missingChanges = [];
             if(changes == null)
                return false;
             for (var i = 0; i < changes.length; i++) {
                 var change = changes[i];
                 var isThisMissing = false;
                 if(change.originalEndLineNumber != 0)
                 {
                    for(var j = change.originalStartLineNumber; j <= change.originalEndLineNumber; j++)
                    {
                    if(typeof lineDecorationsOrginal[j] === 'undefined') {
                    isThisMissing = true;
                    isSomethingMissing = true;
                    }
                    }
                 }
                 if(change.modifiedEndLineNumber != 0)
                 {
                    for(var j = change.modifiedStartLineNumber; j <= change.modifiedEndLineNumber; j++)
                    {
                    if(typeof lineDecorationsModified[j] === 'undefined') {
                    isThisMissing = true;
                    isSomethingMissing = true;
                    }
                    }
                 }
                 if(isThisMissing)
                 {
                    this.missingChanges.push(change);
                 }
             }
             console.log(this.missingChanges);
             var header = this.$refs.header;
             if(!isSomethingMissing && header)
             {
                header.className = "card-header header-valid";
                return true;
             } else {
                header.className = "card-header";
             }
             return false;
        },
        getData: function(hash) {
           var data = {};
           var file = this.file;
           console.log(hash + "_" + file.parent_revision_hash + "_" + file.filename);
           data[hash + "_" + file.parent_revision_hash + "_" + file.filename] = {};
           var lineDecorationsOrginal = this.decorationsObjectsLeft;
           for(var k = 0; k < lineDecorationsOrginal.length; k++) {
                if(typeof lineDecorationsOrginal[k] === 'undefined') {
                    continue;
                }
                var label = lineDecorationsOrginal[k].options.technologies;
                var line = lineDecorationsOrginal[k].range.startLineNumber;
                
                let mappedLine = line
                for(let ml of this.lines) {
                  if(ml['new'] == '-' && ml['old'] == line) {
                    mappedLine = ml['number']
                  }
                }

                data[hash + "_" + file.parent_revision_hash + "_" + file.filename][mappedLine] = label;
           }
           var lineDecorationsModified = this.decorationsObjectsRight;
           for(var k = 0; k < lineDecorationsModified.length; k++) {
                if(typeof lineDecorationsModified[k] === 'undefined') {
                    continue;
                }
                var label = lineDecorationsModified[k].options.technologies;
                var line = lineDecorationsModified[k].range.startLineNumber;

                let mappedLine = line
                for(let ml of this.lines) {
                  if(ml['old'] == '-' && ml['new'] == line) {
                    mappedLine = ml['number']
                  }
                }

                data[hash + "_" + file.parent_revision_hash + "_" + file.filename][mappedLine] = label;
           }
            return data;
        }
      }
}
</script>