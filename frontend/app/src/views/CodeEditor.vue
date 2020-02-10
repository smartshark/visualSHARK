<template>
  <div class="wrapper">
    <div class="animated fadeIn">
          <div class="card">
            <div class="card-header">
              <i class="fa fa-bug"></i> General information
            </div>
            <div class="card-block">

            <div class="row">
<label class="col-sm-2">Revision</label>

<div class="col-sm-10">
            <a href="#">Show 26c458f09bc858537d02b3749868e8318b167a68 on GitHub</a>
            </div>
            </div>

            <div class="row">
<label class="col-sm-2">Issue Links</label>
<div class="col-sm-10">
            <a href="#">IVY-1150</a>
            </div>
            </div>


<div class="row">
<label class="col-sm-2">Commit Message</label>
<div class="col-sm-10">
            <textarea :value="value" class="form-control"></textarea>
            </div>
            </div>
            </div>
          </div>
          <div class="card" v-for="commit in commits">
            <div class="card-header">
              <i class="fa fa-bug"></i> Commit {{ commit.revision_hash }}
            </div>
            <div class="card-block">
            <div v-for="file in commit.files">
            {{ file.path }}
             <MonacoEditor  class="editor"
  :diffEditor="true" :value="file.after" :original="file.before" language="java" ref="editor" />
            </div>
            </div>
          </div>

    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import MonacoEditor from 'vue-monaco'
import rest from '../api/rest'


export default {
    data() {
        return {
            code: '',
            original: '',
            commits: [],
            value: ''
        }
    },
    computed: mapGetters({
        currentProject: 'currentProject',
        projectsVcs: 'projectsVcs',
        projectsIts: 'projectsIts',
        projectsMl: 'projectsMl'
    }),
    mounted() {

        var that = this;

        // Start background request
        this.$store.dispatch('pushLoading')
        rest.getIssueWithCommits('')
            .then(response => {
                this.$store.dispatch('popLoading')
                this.commits = response.data['commits'];
                setTimeout(() => {
                    // Register all editors
                    that.registerFoldingModel();
                    for (var i = 0; i < that.$refs.editor.length; i++) {
                        console.log("Init editor: ", i);
                        that.initEditor(that.$refs.editor[i]);
                    }
                }, 25);
            })
            .catch(e => {
                this.$store.dispatch('pushError', e)
            });
    },
    components: {
        MonacoEditor
    },
    methods: {
        initEditor: function(editor) {
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
        registerFoldingModel: function() {
            var that = this;
            monaco.languages.registerFoldingRangeProvider("java", {
                provideFoldingRanges: function(model, context, token) {
                    var margin = 2;
                    var ranges = [];
                    // Detect editor
                    var editor = null;
                    var isOrginial = false;
                    for (var i = 0; i < that.$refs.editor.length; i++) {
                        var currentEditor = that.$refs.editor[i].getEditor();
                        if (currentEditor.getOriginalEditor().getModel() == model) {
                            editor = currentEditor;
                            isOrginial = true;
                        } else if (currentEditor.getModifiedEditor().getModel() == model) {
                            editor = currentEditor;
                            isOrginial = false;
                        }
                    }
                    var startLine = 1;
                    var changes = editor.getLineChanges();
                    for (var i = 0; i < changes.length; i++) {
                        var change = changes[i];
                        var ende = change.originalStartLineNumber;
                        if (ende > change.modifiedStartLineNumber) {
                            ende = change.modifiedStartLineNumber;
                        }
                        ende = ende - margin;
                        var range = {
                            start: startLine,
                            end: ende,
                            kind: monaco.languages.FoldingRangeKind.Region
                        };
                        ranges.push(range);

                        var newStartLine = change.originalEndLineNumber;
                        if (newStartLine < change.modifiedEndLineNumber) {
                            newStartLine = change.modifiedEndLineNumber;
                        }
                        if (newStartLine == 0) {
                            newStartLine = ende + 1;

                        }
                        startLine = newStartLine + margin;

                    }

                    ranges.push({
                        start: startLine + margin,
                        end: model.getLineCount(),
                        kind: monaco.languages.FoldingRangeKind.Region
                    });
                    return ranges;
                }
            });
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

            var action1 = {
                id: 'my-unique-id',
                label: 'Add Linelabel',
                keybindings: [ // chord
                    monaco.KeyCode.KEY_L
                ],
                precondition: null,
                keybindingContext: null,
                contextMenuGroupId: 'navigation',
                contextMenuOrder: 1.5,
                run: function(ed) {
                    var lineNumber = ed.getPosition().lineNumber;
                    ed.deltaDecorations([], [{
                        range: new monaco.Range(lineNumber, 1, lineNumber, 1),
                        options: {
                            isWholeLine: true,
                            linesDecorationsClassName: 'myLineDecoration'
                        }
                    }, ]);
                    return null;
                }
            };
            editor.getEditor().getOriginalEditor().addAction(action1);
            editor.getEditor().getModifiedEditor().addAction(action1);

            var action2 = {
                id: 'my-unique-id2',
                label: 'Add Linelabel2',
                keybindings: [ // chord
                    monaco.KeyCode.KEY_K
                ],
                precondition: null,
                keybindingContext: null,
                contextMenuGroupId: 'navigation',
                contextMenuOrder: 1.5,
                run: function(ed) {
                    var lineNumber = ed.getPosition().lineNumber;
                    ed.deltaDecorations([], [{
                        range: new monaco.Range(lineNumber, 1, lineNumber, 1),
                        options: {
                            isWholeLine: true,
                            linesDecorationsClassName: 'myLineDecoration2'
                        }
                    }, ]);
                    return null;
                }
            };

            editor.getEditor().getOriginalEditor().addAction(action2);
            editor.getEditor().getModifiedEditor().addAction(action2);
        }
    }
}
</script>

<style>
.editor {
  width: 100% !important;
  height: 800px;
}

.myLineDecoration {
	background: yellow;
	width: 5px !important;
	margin-left: 3px;
}
.myLineDecoration2 {
	background: red;
	width: 5px !important;
	margin-left: 3px;
}
</style>
