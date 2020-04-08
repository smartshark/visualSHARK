<template>
<div>
 <div class="card-header" ref="header" style="margin-top: 20px; border-top:5px solid #000;" :id="'file' + file.filename + file.parent_revision_hash">
 <div style="margin-bottom: 5px;">
            {{ file.filename }}</div>
                      <div class="btn-group" role="group" style="margin-top: 10px; margin-right: 10px;">
  <div style="margin-right: 5px;">Mark file as</div>
     <button class="btn btn-primary" v-on:click="labelWhitespace()" style="background-color:#bbb;">whitespace</button>
     <button class="btn btn-primary" v-on:click="labelDocumentation()" style="background-color:#442727;">documentation</button>
     <button class="btn btn-primary" v-on:click="labelTest()" style="background-color:#2b580c;">test</button>
     <button class="btn btn-primary" v-on:click="labelUnrelated()" style="background-color:#ffbd69;">unrelated</button>


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
             <MonacoEditor  class="editor"
  :diffEditor="true" :value="file.after" :original="file.before" language="java" ref="editor" />
  </div>
</div>
</template>
<script>

import MonacoEditor from 'vue-monaco'

export default {
 data() {
        return {
            decorationsLeft: [],
            decorationsObjectsLeft: [],
            decorationsRight: [],
            decorationsObjectsRight: [],
            missingChanges: [],
            folding: false,
            showValidation: false,
        }
    },
    props: {
    file : Object
    },
    components: {
        MonacoEditor
    },
    methods: {
        getEditor: function() {
            return this.$refs.editor;
        },
        initEditor: function() {
            var editor = this.$refs.editor;
            this.addActionToEditor(editor);
            this.setAutoFolding(editor);
            if(this.folding) {
              this.setFoldingModel(editor);
              this.foldAll(editor);
            }
            this.jumpActions(editor);
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
        clickFoldAll: function() {
            var editor = this.$refs.editor;
            this.foldAll(editor);
        },
        clickUnfoldAll: function() {
            var editor = this.$refs.editor;
            editor.getEditor().getOriginalEditor().trigger('fold', 'editor.unfoldAll');
        },
        foldAll: function(editor) {
            setTimeout(function() {
                editor.getEditor().getOriginalEditor().trigger('fold', 'editor.foldAll');
            }, 1000);
        },
        setFoldingModel: function(editor) {
            var foldingContrib = editor.getEditor().getOriginalEditor().getContribution('editor.contrib.folding');
            var foldingContribModified = editor.getEditor().getModifiedEditor().getContribution('editor.contrib.folding');
            foldingContribModified.getFoldingModel().then(foldingModelModified => {
                foldingContrib.getFoldingModel().then(foldingModel => {
                    foldingModel.onDidChange((e) => {
                        var regions = foldingModel.regions;
                        var regionsModified = foldingModelModified.regions;
                        let toToggle = [];
                        for (let i = regions.length - 1; i >= 0; i--) {
                            if (regions.isCollapsed(i) != regionsModified.isCollapsed(i)) {
                                toToggle.push(regionsModified.toRegion(i));
                            }
                        }
                        foldingModelModified.toggleCollapseState(toToggle);
                    });

                    foldingModelModified.onDidChange((e) => {
                        var regions = foldingModel.regions;
                        var regionsModified = foldingModelModified.regions;
                        let toToggle = [];
                        for (let i = regions.length - 1; i >= 0; i--) {
                            if (regions.isCollapsed(i) != regionsModified.isCollapsed(i)) {
                                toToggle.push(regions.toRegion(i));
                            }
                        }
                        foldingModel.toggleCollapseState(toToggle);
                    });
                });
            });
        },
        setAutoFolding: function(editor) {
            editor.getEditor().updateOptions({	
                ignoreTrimWhitespace: false,	
            });
            editor.getEditor().getModifiedEditor().updateOptions({
                readOnly: true,
                folding: this.folding,
                automaticLayout: true
            });
            editor.getEditor().getOriginalEditor().updateOptions({
                readOnly: true,
                folding: this.folding,
                automaticLayout: true
            });
        },
        addActionToEditor: function(editor) {
           this.addSingleActionToEditor(editor, '1', 'Bugfix', [ monaco.KeyCode.KEY_1 ], 'bugfix');
           this.addSingleActionToEditor(editor, '2', 'Whitespace', [ monaco.KeyCode.KEY_2 ], 'whitespace');
           this.addSingleActionToEditor(editor, '3', 'Documentation', [ monaco.KeyCode.KEY_3 ], 'documentation');
           this.addSingleActionToEditor(editor, '4', 'Refactoring', [ monaco.KeyCode.KEY_4 ], 'refactoring');
           this.addSingleActionToEditor(editor, '5', 'Test', [ monaco.KeyCode.KEY_5 ], 'test');
           this.addSingleActionToEditor(editor, '6', 'Unrelated', [ monaco.KeyCode.KEY_6 ], 'unrelated');
           this.addSingleActionToEditor(editor, '7', 'Remove label', [ monaco.KeyCode.KEY_7 ], '');
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
                     for(var k = 0; k < lineDecorationsOrginal.length; k++)
                     {
                          if(typeof lineDecorationsOrginal[k] === 'undefined') {
                              continue;
                          }
                          var label = lineDecorationsOrginal[k].options.linesDecorationsClassName;
                          var line = lineDecorationsOrginal[k].range.startLineNumber;
                          data[hash + "_" + file.parent_revision_hash + "_" + file.filename][line] = label;
                     }
                     var lineDecorationsModified = this.decorationsObjectsRight;
                     for(var k = 0; k < lineDecorationsModified.length; k++)
                     {
                          if(typeof lineDecorationsModified[k] === 'undefined') {
                              continue;
                          }
                          var label = lineDecorationsModified[k].options.linesDecorationsClassName;
                          var line = lineDecorationsModified[k].range.startLineNumber;
                          data[hash + "_" + file.parent_revision_hash + "_" + file.filename][line] = label;
                     }
            return data;
        },
        labelWhitespace: function() {
          this.labelFileComplete('whitespace');
        },
        labelDocumentation: function() {
          this.labelFileComplete('documentation');
        },
        labelTest: function() {
          this.labelFileComplete('test');
        },
        labelUnrelated: function() {
          this.labelFileComplete('unrelated');
        },
        labelFileComplete: function(className) {
             var changes = this.$refs.editor.getEditor().getLineChanges();
             console.log(this.$refs.editor.getEditor());
             for (var i = 0; i < changes.length; i++) {
                 var change = changes[i];

                 for(var j = change.originalStartLineNumber; j <= change.originalEndLineNumber; j++) {

                 this.decorationsObjectsLeft[j] = {
                        range: new monaco.Range(j, 1, j, 1),
                        options: {
                            isWholeLine: true,
                            linesDecorationsClassName: className
                        },
                        change: change
                 };

                 this.decorationsLeft = this.$refs.editor.getEditor().getOriginalEditor().deltaDecorations(this.decorationsLeft, Object.values(this.decorationsObjectsLeft));
                 this.validateEditor();
                 }

                 for(var j = change.modifiedStartLineNumber; j <= change.modifiedEndLineNumber; j++) {

                 this.decorationsObjectsRight[j] = {
                        range: new monaco.Range(j, 1, j, 1),
                        options: {
                            isWholeLine: true,
                            linesDecorationsClassName: className
                        },
                        change: change
                 };

                 this.decorationsRight = this.$refs.editor.getEditor().getModifiedEditor().deltaDecorations(this.decorationsRight, Object.values(this.decorationsObjectsRight));
                 this.validateEditor();
                 }

             }
        }
    }
}
</script>

