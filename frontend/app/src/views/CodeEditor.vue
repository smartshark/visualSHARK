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
            <textarea class="form-control">FIX: Artifact report throws NPE when artifact is not in cache (IVY-1150) (thanks to Steve Jones)

git-svn-id: https://svn.apache.org/repos/asf/ant/ivy/core/trunk@892370 13f79535-47bb-0310-9956-ffa450edef68</textarea>
            </div>
            </div>
            </div>
          </div>
          <div class="card">
            <div class="card-header">
              <i class="fa fa-bug"></i> Changes
            </div>
            <div class="card-block">
             <MonacoEditor class="editor"
  :diffEditor="true" :value="code" :original="original" language="java" ref="editor" />
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
  data () {
    return {
      code: '',
      original: ''
    }
  },
  mounted () {

 this.$store.dispatch('pushLoading')
      rest.getIssueWithCommits('')
        .then(response => {
          this.$store.dispatch('popLoading')
          console.log(response.data['commits'][0]["files"][0]['after'])
          var original = response.data['commits'][0]["files"][0]['before']
          var code = response.data['commits'][0]["files"][0]['after']
          var originalModel = monaco.editor.createModel(original, "java");
          var modifiedModel = monaco.editor.createModel(code, "java");


          window.editor.getEditor().setModel({
	original: originalModel,
	modified: modifiedModel
});

setTimeout(function() {
window.editor.getEditor().getOriginalEditor().trigger('fold', 'editor.foldAll');
}, 1000);

        })
        .catch(e => {
          this.$store.dispatch('pushError', e)
        })

  var that2 = this;
  window.editor = this.$refs.editor;
  console.log("That2 log:");
  console.log(that2);
  var margin = 2;

  monaco.languages.registerFoldingRangeProvider("java", {
    provideFoldingRanges: function(model, context, token) {
        var ranges = [];
        console.log(model);
        console.log(context);
        console.log(that2);
        var startLine = 1;
        var isOrginial = window.editor.getEditor().getOriginalEditor().getModel() == model;
        var changes = window.editor.getEditor().getLineChanges();
        for(var i = 0; i < changes.length; i++)
        {
          var change = changes[i];
          var ende = change.originalStartLineNumber;
          if(ende > change.modifiedStartLineNumber)
          {
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
          if(newStartLine < change.modifiedEndLineNumber)
          {
             newStartLine = change.modifiedEndLineNumber;
          }
          if(newStartLine == 0)
          {
             newStartLine = ende +1;

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

     var ed = this.$refs.editor.getEditor().getOriginalEditor();
     var decorations = [];
window.editor1 = this.$refs.editor;

this.$refs.editor.getEditor().getModifiedEditor().updateOptions({ readOnly: true, folding: true, automaticLayout: true  });
this.$refs.editor.getEditor().getOriginalEditor().updateOptions({ readOnly: true, folding: true,  automaticLayout: true  });

var action1  = {
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
};
this.$refs.editor.getEditor().getOriginalEditor().addAction(action1);
this.$refs.editor.getEditor().getModifiedEditor().addAction(action1);

var action2  = {
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
};

this.$refs.editor.getEditor().getOriginalEditor().addAction(action2);
this.$refs.editor.getEditor().getModifiedEditor().addAction(action2);

var foldingContrib = that2.$refs.editor.getEditor().getOriginalEditor().getContribution('editor.contrib.folding');
var foldingContribModified = that2.$refs.editor.getEditor().getModifiedEditor().getContribution('editor.contrib.folding');
foldingContribModified.getFoldingModel().then(foldingModelModified => {
  foldingContrib.getFoldingModel().then(foldingModel => {
    foldingModel.onDidChange((e) => {
      var regions = foldingModel.regions;
      var regionsModified = foldingModelModified.regions;
	    let toToggle = [];
    	for (let i = regions.length - 1; i >= 0; i--) {
    	   if(regions.isCollapsed(i) != regionsModified.isCollapsed(i))
    	   {
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
    	   if(regions.isCollapsed(i) != regionsModified.isCollapsed(i))
    	   {
    	   toToggle.push(regions.toRegion(i));
    	   }
    	}
    	foldingModel.toggleCollapseState(toToggle);
    });
  });
 });
setTimeout(function() {
that2.$refs.editor.getEditor().getOriginalEditor().trigger('fold', 'editor.foldAll');
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
