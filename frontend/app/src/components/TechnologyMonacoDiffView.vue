<template>
<div>
  <div class="card-header" ref="header" :id="'file' + file.filename + file.parent_revision_hash">
    <div style="margin-bottom: 5px;">{{ file.filename }}</div>
    <div>
      <div class="label">
        Selected lines <template v-if="currentRange">{{currentRange.length}}</template><multiselect :id="'technologySelector' + file.filename + file.parent_revision_hash" v-model="selectedTechnologies" @tag="addTechnology" :taggable="true" :options="technologies" :multiple="true" placeholder="select technologies"></multiselect>
        <button v-if="currentRange.length > 0" v-on:click="setTechnologies()" class="btn btn-primary">Set</button>
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

// we override this stuff from the monaco editor to get the correct diffs
var LineChange = /** @class */ (function () {
    function LineChange(originalStartLineNumber, originalEndLineNumber, modifiedStartLineNumber, modifiedEndLineNumber, charChanges) {
        this.originalStartLineNumber = originalStartLineNumber;
        this.originalEndLineNumber = originalEndLineNumber;
        this.modifiedStartLineNumber = modifiedStartLineNumber;
        this.modifiedEndLineNumber = modifiedEndLineNumber;
        this.charChanges = charChanges;
    }
    LineChange.createFromDiffResult = function (shouldIgnoreTrimWhitespace, diffChange, originalLineSequence, modifiedLineSequence, continueProcessingPredicate, shouldComputeCharChanges, shouldPostProcessCharChanges) {
        var originalStartLineNumber;
        var originalEndLineNumber;
        var modifiedStartLineNumber;
        var modifiedEndLineNumber;
        var charChanges = undefined;
        if (diffChange.originalLength === 0) {
            originalStartLineNumber = originalLineSequence.getStartLineNumber(diffChange.originalStart) - 1;
            originalEndLineNumber = 0;
        }
        else {
            originalStartLineNumber = originalLineSequence.getStartLineNumber(diffChange.originalStart);
            originalEndLineNumber = originalLineSequence.getEndLineNumber(diffChange.originalStart + diffChange.originalLength - 1);
        }
        if (diffChange.modifiedLength === 0) {
            modifiedStartLineNumber = modifiedLineSequence.getStartLineNumber(diffChange.modifiedStart) - 1;
            modifiedEndLineNumber = 0;
        }
        else {
            modifiedStartLineNumber = modifiedLineSequence.getStartLineNumber(diffChange.modifiedStart);
            modifiedEndLineNumber = modifiedLineSequence.getEndLineNumber(diffChange.modifiedStart + diffChange.modifiedLength - 1);
        }
        if (shouldComputeCharChanges && diffChange.originalLength !== 0 && diffChange.modifiedLength !== 0 && continueProcessingPredicate()) {
            var originalCharSequence = originalLineSequence.getCharSequence(shouldIgnoreTrimWhitespace, diffChange.originalStart, diffChange.originalStart + diffChange.originalLength - 1);
            var modifiedCharSequence = modifiedLineSequence.getCharSequence(shouldIgnoreTrimWhitespace, diffChange.modifiedStart, diffChange.modifiedStart + diffChange.modifiedLength - 1);
            var rawChanges = computeDiff(originalCharSequence, modifiedCharSequence, continueProcessingPredicate, true, null);
            if (shouldPostProcessCharChanges) {
                rawChanges = postProcessCharChanges(rawChanges);
            }
            charChanges = [];
            for (var i = 0, length_2 = rawChanges.length; i < length_2; i++) {
                charChanges.push(CharChange.createFromDiffChange(rawChanges[i], originalCharSequence, modifiedCharSequence));
            }
        }
        return new LineChange(originalStartLineNumber, originalEndLineNumber, modifiedStartLineNumber, modifiedEndLineNumber, charChanges);
    };
    return LineChange;
}());

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
        selectedTechnologyType: 'per-line',
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
        return [...new Set(this.existingTechnologies.concat(this.addedTechnologies))]  // we still need this because emitting newTechnology resets the array
      },
      editorOptions: function () {
        return {readOnly: this.readOnly}
      },
      editorLanguage: function () {
        if(this.file.filename.endsWith('.java')) {
          return "java"
        }else if(this.file.filename.endsWith('.xml')) {
          return "xml"
        }else if(this.file.filename.endsWith('.cs')) {
          return "csharp"
        }else if(this.file.filename.endsWith('.xaml')) {
          return "xaml"
        }else {
          return ""
        }
      }
    },
    methods: {
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
        editorWillMount(monaco) {
          this.$emit('editorWillMount', monaco)
        },
        isModified(lineNumber, isOriginal) {
          return (isOriginal && this.getOriginalChangeForLine(lineNumber) !== null) || (!isOriginal && this.getModifiedChangeForLine(lineNumber) !== null)
        },
        getTechnologiesForLine(lineNumber, isOriginal) {
          let ret = {'techs': [], 'type': ''}
          if(isOriginal && typeof this.decorationsObjectsLeft[lineNumber] !== 'undefined') {
              ret['techs'] = this.decorationsObjectsLeft[lineNumber].options.technologies
              ret['type'] = this.decorationsObjectsLeft[lineNumber].options.linesDecorationsClassName
          }
          if(!isOriginal && typeof this.decorationsObjectsRight[lineNumber] !== 'undefined') {
              ret['techs'] = this.decorationsObjectsRight[lineNumber].options.technologies
              ret['type'] = this.decorationsObjectsRight[lineNumber].options.linesDecorationsClassName
          }
          return ret
        },
        setTechnologiesForLine(lineNumber, isOriginal, techs, selectionType) {
          if(isOriginal && typeof this.decorationsObjectsLeft[lineNumber] !== 'undefined') {
            this.decorationsObjectsLeft[lineNumber].options.technologies = techs.join()
            this.decorationsObjectsLeft[lineNumber].options.linesDecorationsClassName = selectionType
          }
          if(isOriginal && typeof this.decorationsObjectsLeft[lineNumber] === 'undefined') {
            this.decorationsObjectsLeft[lineNumber] = {
              range: new monaco.Range(lineNumber, 1, lineNumber, 1),
              options: {
                    isWholeLine: true,
                    linesDecorationsClassName: selectionType,
                    technologies: techs.join()
                }
              }
          }
          if(!isOriginal && typeof this.decorationsObjectsRight[lineNumber] !== 'undefined') {
              this.decorationsObjectsRight[lineNumber].options.technologies = techs.join()
              this.decorationsObjectsRight[lineNumber].options.linesDecorationsClassName = selectionType
          }
          if(!isOriginal && typeof this.decorationsObjectsRight[lineNumber] === 'undefined') {
            this.decorationsObjectsRight[lineNumber] = {
              range: new monaco.Range(lineNumber, 1, lineNumber, 1),
              options: {
                    isWholeLine: true,
                    linesDecorationsClassName: selectionType,
                    technologies: techs.join()
                }
              }
          }
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
          
          let dec = this.selectedTechnologyType
          let techs = this.selectedTechnologies.join()
          if(this.selectedTechnologies.length === 0) {
            dec = ''
            techs = null
          }
          console.log('setting tech type', dec)
          if(isOriginal) {  
            for(let lineNumber of this.currentRange) {
              let hunk = this.getOriginalChangeForLine(lineNumber)
              this.decorationsObjectsLeft[lineNumber] = {
                range: new monaco.Range(lineNumber, 1, lineNumber, 1),
                options: {
                    isWholeLine: true,
                    linesDecorationsClassName: dec,
                    technologies: techs
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
                    linesDecorationsClassName: dec,  // this.selectedTechnologies.join()
                    technologies: techs
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
          this.$emit('addTechnology', newTechnology)
        },
        getEditor: function() {
            return this.$refs.editor;
        },
        initEditor: function() {
            var editor = this.$refs.editor;
            this.addActionToEditor(editor);
            this.jumpActions(editor);

            console.log('editor line changes', editor.getEditor().getLineChanges())
            let edref = editor.getEditor()
            //edref._diffComputationResult = {changes: LineChange.createFromDiffResult(true, edref.getOriginalEditor().getModel().uri, edref.getModifiedEditor().getModel().uri, this.file.after, null, false, false)}
            edref._diffComputationResult = {changes: this.calculateLineChanges(this.file.hunks)}
            //console.log(this.file.hunks)
            edref._beginUpdateDecorations = function() {
              //console.log('i should update');
            }
            //console.log('editor line changes2', editor.getEditor().getLineChanges())

            console.log('show me the money!')
            console.log(this.file)
            var labelCssClass = ['per-line', 'per-block'];
            for(var i = 0; i < this.file.lines.length; i++)
            {
              var line = this.file.lines[i];
              if(line.label > 0) {
                labelCssClass = line.techs['selectionType']
                
                if(line.techs !== 'undefined') {
                  if(line.new == '-') {
                    this.setTechnologiesForLine(line.old, true, line.techs['technologies'], line.techs['selectionType'])
                  }
                  if(line.old == '-') {
                    this.setTechnologiesForLine(line.new, false, line.techs['technologies'], line.techs['selectionType'])
                  }
                }

/*                var label = labelCssClass[line.label-1];
                this.markLineInEditorLeft(line.old, labelCssClass,this.$refs.editor,this.$refs.editor.getEditor().getOriginalEditor());
                this.markLineInEditorRight(line.new, labelCssClass,this.$refs.editor,this.$refs.editor.getEditor().getModifiedEditor());*/
              }
/*              if(typeof line.techs !== 'undefined' && line.techs.length > 0) {
                if(line.new == '-') {
                  this.setTechnologiesForLine(line.old, true, line.techs['technologies'], line.techs['selectionType'])
                }
                if(line.old == '-') {
                  this.setTechnologiesForLine(line.new, false, line.techs['technologies'], line.techs['selectionType'])
                }
              }*/
            }
          this.decorationsLeft = edref.getOriginalEditor().deltaDecorations(this.decorationsLeft, Object.values(this.decorationsObjectsLeft));
          this.decorationsRight = edref.getModifiedEditor().deltaDecorations(this.decorationsRight, Object.values(this.decorationsObjectsRight));
          this.validateEditor()
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
        labelTechnologyAction: function(editor, ed, label) {
          const range = ed.getSelection()
          const isOriginal = ed === this.$refs.editor.getEditor().getOriginalEditor()
          let lines = []

          for(let hunk of editor.getEditor().getLineChanges()) {
            for(let lineNumber = range.startLineNumber; lineNumber <= range.endLineNumber; lineNumber++) {

              // are changed lines part of the hunk lines?
              if(isOriginal) {
                if(hunk.originalStartLineNumber <= lineNumber && lineNumber <= hunk.originalEndLineNumber) {
                  //lines.push(lineNumber)
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
            this.selectedTechnologyType = label
            document.getElementById("technologySelector" + this.file.filename + this.file.parent_revision_hash).focus();
          }
          return null
        },
        addActionToEditor: function(editor) {
          this.addSingleActionToEditor2(editor, '1', 'Set technologies', [ monaco.KeyCode.KEY_1 ], 'per-line')
          this.addSingleActionToEditor2(editor, '2', 'Set technologies separately', [ monaco.KeyCode.KEY_2 ], 'per-block')
          this.addSingleActionToEditor(editor, '7', 'Remove technologies', [ monaco.KeyCode.KEY_7 ], '');
        },
        markLineInEditorLeft(lineNumber, className, editor, ed, techs) {
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
        addSingleActionToEditor2: function(editor, id, label, keybindings, cssClass) {
          let actionLeft = {
            id: id,
            label: label,
            keybindings: keybindings,
            precondition: null,
            keybindingContext: null,
            contextMenuGroupId: 'navigation',
            contextMenuOrder: id,
            run: (ed) => {
              this.labelTechnologyAction(editor, ed, cssClass)
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
        getData: function() {
           var data = {};
           var file = this.file;
           data[file.filename] = {};
           var lineDecorationsOrginal = this.decorationsObjectsLeft;
           for(var k = 0; k < lineDecorationsOrginal.length; k++) {
                if(typeof lineDecorationsOrginal[k] === 'undefined') {
                    continue;
                }
                var techs = lineDecorationsOrginal[k].options.technologies;
                var cssClass = lineDecorationsOrginal[k].options.linesDecorationsClassName;
                var line = lineDecorationsOrginal[k].range.startLineNumber;
                
                let mappedLine = line
                for(let ml of this.lines) {
                  if(ml['new'] == '-' && ml['old'] == line) {
                    mappedLine = ml['number']
                  }
                }

                data[file.filename][mappedLine] = {'technologies': techs, 'selectionType': cssClass};
           }
           var lineDecorationsModified = this.decorationsObjectsRight;
           for(var k = 0; k < lineDecorationsModified.length; k++) {
                if(typeof lineDecorationsModified[k] === 'undefined') {
                    continue;
                }
                var techs = lineDecorationsModified[k].options.technologies;
                var cssClass = lineDecorationsModified[k].options.linesDecorationsClassName;
                var line = lineDecorationsModified[k].range.startLineNumber;

                let mappedLine = line
                for(let ml of this.lines) {
                  if(ml['old'] == '-' && ml['new'] == line) {
                    mappedLine = ml['number']
                  }
                }

                data[file.filename][mappedLine] = {'technologies': techs, 'selectionType': cssClass};
           }
            return data;
        }
      }
}
</script>