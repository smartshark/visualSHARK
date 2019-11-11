<template>
  <div class="wrapper">
    <div class="animated fadeIn">
          <div class="card">
            <div class="card-header">
              <i class="fa fa-bug"></i> Issues
            </div>
            <div class="card-block">
             <MonacoEditor class="editor"
  :diffEditor="true" :value="code" :original="original" language="foldLanguage" ref="editor" />
            </div>
          </div>

    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import MonacoEditor from 'vue-monaco'



export default {
  data () {
  var jsCode = [
	'"use strict";',
	'function Person(age) {',
	'	if (age) {',
	'		this.age = age;',
	'	}',
	'}',
	'Person.prototype.getAge = function () {',
	'	return this.age;',
	'};'
].join('\n');

var jsCode2 = [
	'"use strict";',
	'function Person(age) {',
	'	if (age) {',
	'		this.age = age;',
	'	}',
	'}',
	'Person.prototsdfsdfype.getAgedfsdf = function () {',
	'	return this.age;',
	'};',
	'"use strict";',
	'function Person(age) {',
	'	if (age) {',
	'		this.age = age;',
	'	}',
	'}',
	'Person.prototsdfsdfype.getAgedfsdf = function () {',
	'	return this.age;',
	'};',
	'"use strict";',
	'function Person(age) {',
	'	if (age) {',
	'		this.age = age;',
	'	}',
	'}',
	'Person.prototsdfsdfype.getAgedfsdf = function () {',
	'	return this.age;',
	'};'
].join('\n');

    return {
      code: jsCode,
      original: jsCode2
    }
  },
  mounted () {
monaco.languages.register({
    id: "foldLanguage"
});
  var that2 = this.$refs;

  monaco.languages.registerFoldingRangeProvider("foldLanguage", {
    provideFoldingRanges: function(model, context, token) {
        var ranges = [];
        var startLine = 1;
        var changes = that2.editor.getEditor().getLineChanges();
        for(var i = 0; i < changes.length; i++)
        {
          var change = changes[i];
          ranges.push({
                start: startLine,
                end: change.originalStartLineNumber -1,
                kind: monaco.languages.FoldingRangeKind.Region
          });
          startLine = change.originalEndLineNumber +1;
          console.log(change);
        }

        ranges.push({
                start: startLine,
                end: model.getLineCount(),
                kind: monaco.languages.FoldingRangeKind.Region
        });
        console.log(ranges);
        return ranges;
    }
});
     var ed = this.$refs.editor.getEditor().getOriginalEditor();
     var decorations = this.$refs.editor.getEditor().getOriginalEditor().deltaDecorations([], [
	{ range: new monaco.Range(1,1,3,1), options: { isWholeLine: true, linesDecorationsClassName: 'myLineDecoration' }},
]);
window.editor1 = this.$refs.editor;

this.$refs.editor.getEditor().getOriginalEditor().updateOptions({ readOnly: true, folding: true, language: "foldLanguage" });
this.$refs.editor.getEditor().getOriginalEditor().addAction({
	// An unique identifier of the contributed action.
	id: 'my-unique-id',

	// A label of the action that will be presented to the user.
	label: 'Add Linelabel',

	// An optional array of keybindings for the action.
	keybindings: [		// chord
		 monaco.KeyCode.KEY_L
	],

	// A precondition for this action.
	precondition: null,

	// A rule to evaluate on top of the precondition in order to dispatch the keybindings.
	keybindingContext: null,

	contextMenuGroupId: 'navigation',

	contextMenuOrder: 1.5,

	// Method that will be executed when the action is triggered.
	// @param editor The editor instance is passed in as a convinience
	run: function(ed) {
	  var lineNumber = ed.getPosition().lineNumber;
	  ed.deltaDecorations([], [
	{ range: new monaco.Range(lineNumber,1,lineNumber,1), options: { isWholeLine: true, linesDecorationsClassName: 'myLineDecoration' }},
]);
		return null;
	}
});

this.$refs.editor.getEditor().getModifiedEditor().updateOptions({ readOnly: true });
this.$refs.editor.getEditor().getOriginalEditor().addAction({
	// An unique identifier of the contributed action.
	id: 'my-unique-id2',

	// A label of the action that will be presented to the user.
	label: 'Add Linelabel2',

	// An optional array of keybindings for the action.
	keybindings: [		// chord
		 monaco.KeyCode.KEY_K
	],

	// A precondition for this action.
	precondition: null,

	// A rule to evaluate on top of the precondition in order to dispatch the keybindings.
	keybindingContext: null,

	contextMenuGroupId: 'navigation',

	contextMenuOrder: 1.5,

	// Method that will be executed when the action is triggered.
	// @param editor The editor instance is passed in as a convinience
	run: function(ed) {
	  var lineNumber = ed.getPosition().lineNumber;
	  ed.deltaDecorations([], [
	{ range: new monaco.Range(lineNumber,1,lineNumber,1), options: { isWholeLine: true, linesDecorationsClassName: 'myLineDecoration2' }},
]);
		return null;
	}
});

setTimeout(function() {
that2.editor.getEditor().getOriginalEditor().trigger('fold', 'editor.foldAll');
}, 1000);

  },
  components: {
    MonacoEditor
  },
  computed: mapGetters({
    currentProject: 'currentProject',
    projectsVcs: 'projectsVcs',
    projectsIts: 'projectsIts',
    projectsMl: 'projectsMl'
  })
}
</script>

<style>
.editor {
  width: 100%;
  height: 800px;
}

.myLineDecoration {
	background: lightblue;
	width: 5px !important;
	margin-left: 3px;
}
.myLineDecoration2 {
	background: red;
	width: 5px !important;
	margin-left: 3px;
}
</style>
