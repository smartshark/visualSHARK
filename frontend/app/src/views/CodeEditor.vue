<template>
  <div class="wrapper">
    <div class="animated fadeIn">
     <div class="card">
            <div class="card-header">
              <i class="fa fa-tag"></i> Labels
            </div>
            <div class="card-block">
                <div class="label"><span class="dot" style="background-color: #84142d;">1</span>bug fix</div>
                <div class="label"><span class="dot">2</span>whitespace or comment</div>
                <div class="label"><span class="dot" style="background-color: #142850;">3</span>refactoring</div>
                <div class="label"><span class="dot" style="background-color: #ffbd69;">4</span>unrelated</div>
                <div>Press the key of the color to label the current line with the belonging label, press 5 to remove the label</div>
            </div>
      </div>
          <div class="card">
            <div class="card-header">
              <i class="fa fa-bug"></i> General information
            </div>
            <div class="card-block">

            <div class="row">
<label class="col-sm-2">Issue title</label>

<div class="col-sm-10">
            <a href="#">{{ issue.title }}</a>
            </div>
            </div>


<div class="row">
<label class="col-sm-2">Issue description</label>
<div class="col-sm-10">
            <pre class="form-control">{{ issue.desc }}</pre>
            </div>
            </div>
                        <div class="row">
<label class="col-sm-2">Commits</label>
<div class="col-sm-10">
            <button v-for="commit in commits" v-on:click="scrollToCommit(commit)" class="btn btn-default" style="margin-right: 5px;">{{ commit.revision_hash }}</button>
            </div>
            </div>
            <button class="btn btn-primary" v-on:click="submitLabels()" style="float: right;">Submit labels</button>
            </div>
          </div>
          <div class="card" v-for="commit in commits" :id="commit.revision_hash" >
            <div class="card-header">
             <a role="button" data-toggle="collapse" v-on:click="scrollToCommit(commit)" aria-expanded="false" aria-controls="collapseExample">
              <i class="fa fa-bug"></i> Commit {{ commit.revision_hash }} <button class="btn btn-primary" v-on:click="top()" style="float: right;">Jump to top</button>
              </a>
            </div>
            <div :id="'collapse' + commit.revision_hash">
            <div class="card-block">
<div class="row">
<label class="col-sm-2">Commit Message</label>
<div class="col-sm-10">
            <pre class="form-control">{{ commit.message }}</pre>
            </div>
            </div>
            <div v-for="file in commit.files">
            <div class="card-header" ref="header" style="margin-top: 20px; border-top:5px solid #000;">
            {{ file.path }} <button class="btn btn-primary" v-on:click="top()" style="float: right;">Jump to top</button>
            </div>
            <div>
             <MonacoEditor  class="editor"
  :diffEditor="true" options={this.options} :value="file.after" :original="file.before" language="java" ref="editor" />
  </div>
            </div>
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
            commits: [],
            issue: '',
            decorationsLeft: [],
            decorationsObjectsLeft: [],
            decorationsRight: [],
            decorationsObjectsRight: [],
            options: {
      ignoreTrimWhitespace: false
          }
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
                this.issue = response.data['issue'];
                setTimeout(() => {
                    // Register all editors
                    that.registerFoldingModel();
                    for (var i = 0; i < that.$refs.editor.length; i++) {
                        console.log("Init editor: ", i);
                        that.decorationsLeft[i] = [];
                        that.decorationsObjectsLeft[i] = [];
                        that.decorationsRight[i] = [];
                        that.decorationsObjectsRight[i] = [];
                        that.initEditor(i, that.$refs.editor[i]);
                    }
                    that.validateAll();
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
        scrollToCommit : function(commit) {
            document.getElementById('collapse' + commit.revision_hash).style.display = "block";
            document.getElementById(commit.revision_hash).scrollIntoView();
        },
        top : function() {
            scroll(0,0)
        },
        initEditor: function(i, editor) {
            this.addActionToEditor(i, editor);
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
        addActionToEditor: function(i, editor) {
           this.addSingleActionToEditor(i, editor, '1', 'Bugfix', [ monaco.KeyCode.KEY_1 ], 'bugfix');
           this.addSingleActionToEditor(i, editor, '2', 'Whitespace or comment', [ monaco.KeyCode.KEY_2 ], 'whitespace');
           this.addSingleActionToEditor(i, editor, '3', 'Test', [ monaco.KeyCode.KEY_3 ], 'test');
           this.addSingleActionToEditor(i, editor, '4', 'Unrelated', [ monaco.KeyCode.KEY_4 ], 'unrelated');
           this.addSingleActionToEditor(i, editor, '5', 'Remove label', [ monaco.KeyCode.KEY_5 ], '');
        },
        addSingleActionToEditor: function(c, editor, id, label, keybindings, className) {
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
                      delete that.decorationsObjectsLeft[c][lineNumber];
                    } else {
                    that.decorationsObjectsLeft[c][lineNumber] = {
                        range: new monaco.Range(lineNumber, 1, lineNumber, 1),
                        options: {
                            isWholeLine: true,
                            linesDecorationsClassName: className
                        },
                        change: foundChange
                    };
                    }

                    that.decorationsLeft[c] = ed.deltaDecorations(that.decorationsLeft[c], Object.values(that.decorationsObjectsLeft[c]));
                        that.validateAll();
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
                      delete that.decorationsObjectsRight[c][lineNumber];
                    } else {
                    that.decorationsObjectsRight[c][lineNumber] = {
                        range: new monaco.Range(lineNumber, 1, lineNumber, 1),
                        options: {
                            isWholeLine: true,
                            linesDecorationsClassName: className
                        },
                        change: foundChange
                    };
                    }

                    that.decorationsRight[c] = ed.deltaDecorations(that.decorationsRight[c], Object.values(that.decorationsObjectsRight[c]));
                        that.validateAll();
                    }

                    return null;
                }
            };
            editor.getEditor().getModifiedEditor().addAction(actionRight);
        },
        validateAll: function () {
            var that = this;
            setTimeout(() => {
                    for (var i = 0; i < that.$refs.editor.length; i++) {
                        that.validateEditor(that.$refs.editor[i], i);
                    }
             }, 1000);
        },
        validateEditor: function(editor, c) {
             var changes = editor.getEditor().getLineChanges();
             var isSomethingMissing = false;
             var lineDecorationsOrginal = this.decorationsObjectsLeft[c];
             var lineDecorationsModified = this.decorationsObjectsRight[c];
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
             var header = this.$refs.header[c];
             if(!isSomethingMissing && header)
             {
                header.className = "card-header header-valid";
                return true;
             } else {
                header.className = "card-header";
             }
             return false;
        },
        submitLabels : function() {
             // check if anything is missing
             var correct = true;
             for (var i = 0; i < this.$refs.editor.length; i++) {
                  correct = this.validateEditor(this.$refs.editor[i], i) && correct;
             }
             if(!correct)
             {
                // alert("Some labels are missing");
                // return;
             }
             // else collect data for transmit
             var data = {};
             var c = 0;
             for (var i = 0; i < this.commits.length; i++) {
                  var commit = this.commits[i];
                  var hash = commit.id;
                  data[hash] = {};
                  for(var j = 0; j < commit.files.length; j++)
                  {
                     var file = commit.files[j];
                     console.log(file);
                     data[hash][file.id] = [];
                     var lineDecorationsOrginal = this.decorationsObjectsLeft[c];
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
                          data[hash][file.id].push(dataPerLabel);
                     }
                     var lineDecorationsModified = this.decorationsObjectsRight[c];
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
                          data[hash][file.id].push(dataPerLabel);
                     }
                     c++;
                  }
            }
            console.log(data);
            this.$store.dispatch('pushLoading')
            rest.saveLabelsOfCommits({ data :data})
            .then(response => {
                this.$store.dispatch('popLoading')

            })
            .catch(e => {
                this.$store.dispatch('pushError', e)
            });
        }
    }
}
</script>

<style>
.editor {
  width: 100% !important;
  height: 800px;
}

.header-valid {
  background-color: #57e84b;
}

.label {
display: inline-flex;
align-items: center;
}
.dot {
  margin: 2px;
  height: 25px;
  width: 25px;
  background-color: #bbb;
  border-radius: 50%;
  display: inline-block;
  color: white;
  text-align: center;
  padding-top: 2px;
}

.bugfix {
	background: #84142d;
	width: 5px !important;
	margin-left: 3px;
}
.whitespace {
  background-color: #bbb;
	width: 5px !important;
	margin-left: 3px;
}
.test {
  background-color: #142850;
	width: 5px !important;
	margin-left: 3px;
}
.unrelated {
  background-color: #ffbd69;
	width: 5px !important;
	margin-left: 3px;
}
</style>
