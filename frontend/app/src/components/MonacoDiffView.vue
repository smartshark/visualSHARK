<template>
<div>
 <div class="card-header" ref="header" style="margin-top: 20px; border-top:5px solid #000;">
            {{ file.filename }} <button class="btn btn-primary" v-on:click="top()" style="float: right;">Jump to top</button> <button class="btn btn-default" v-on:click="labelTest()" style="float: right;">Label as test</button>
 </div>
        <div>
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
            this.setFoldingModel(editor);
            this.foldAll(editor);
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
                folding: true,
                automaticLayout: true
            });
            editor.getEditor().getOriginalEditor().updateOptions({
                readOnly: true,
                folding: true,
                automaticLayout: true
            });
        },
        addActionToEditor: function(editor) {
           this.addSingleActionToEditor(editor, '1', 'Bugfix', [ monaco.KeyCode.KEY_1 ], 'bugfix');
           this.addSingleActionToEditor(editor, '2', 'Whitespace or comment', [ monaco.KeyCode.KEY_2 ], 'whitespace');
           this.addSingleActionToEditor(editor, '3', 'Test', [ monaco.KeyCode.KEY_3 ], 'test');
           this.addSingleActionToEditor(editor, '4', 'Unrelated', [ monaco.KeyCode.KEY_4 ], 'unrelated');
           this.addSingleActionToEditor(editor, '5', 'Remove label', [ monaco.KeyCode.KEY_5 ], '');
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
                    var lineNumber = ed.getPosition().lineNumber;
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
                    var lineNumber = ed.getPosition().lineNumber;
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
             for (var i = 0; i < changes.length; i++) {
                 var change = changes[i];
                 if(change.originalEndLineNumber != 0)
                 {
                    for(var j = change.originalStartLineNumber; j <= change.originalEndLineNumber; j++)
                    {
                    if(typeof lineDecorationsOrginal[j] === 'undefined') {
                    isSomethingMissing = true;
                    }
                    }
                 }
                 if(change.modifiedEndLineNumber != 0)
                 {
                    for(var j = change.modifiedStartLineNumber; j <= change.modifiedEndLineNumber; j++)
                    {
                    if(typeof lineDecorationsModified[j] === 'undefined') {
                    isSomethingMissing = true;
                    }
                    }
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
                          var dataPerLabel = {};
                          dataPerLabel["label"] = lineDecorationsOrginal[k].options.linesDecorationsClassName;
                          dataPerLabel["line"] = lineDecorationsOrginal[k].range.startLineNumber;
                          dataPerLabel["change"] = lineDecorationsOrginal[k].change;
                          dataPerLabel["modified"] =false;
                          data[hash + "_" + file.parent_revision_hash + "_" + file.filename][dataPerLabel["line"]] = dataPerLabel;
                     }
                     var lineDecorationsModified = this.decorationsObjectsRight;
                     for(var k = 0; k < lineDecorationsModified.length; k++)
                     {
                          if(typeof lineDecorationsModified[k] === 'undefined') {
                              continue;
                          }
                          var dataPerLabel = {};
                          dataPerLabel["label"] = lineDecorationsModified[k].options.linesDecorationsClassName;
                          dataPerLabel["line"] = lineDecorationsModified[k].range.startLineNumber;
                          dataPerLabel["change"] = lineDecorationsModified[k].change;
                          dataPerLabel["modified"] =true;
                          data[hash + "_" + file.parent_revision_hash + "_" + file.filename][dataPerLabel["line"]] = dataPerLabel;
                     }
            return data;
        },
        labelTest: function() {
             var className = 'test';
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

