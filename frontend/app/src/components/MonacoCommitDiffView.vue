<template>
<div class="card" :id="commit.revision_hash">
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
            <template v-for="c in commit.changes">
                <MonacoDiffView :file="c" ref="diffView" />
            </template>
            </div>
            </div>
            </div>
</template>
<script>

import MonacoDiffView from '@/components/MonacoDiffView.vue'

export default {
    components: {
        MonacoDiffView
    },
    props: {
    commit : Object
    },
    methods: {
        top : function() {
            scroll(0,0)
        },
        initEditors: function() {
            for(var i = 0; i < this.$refs.diffView.length; i++)
            {
                this.$refs.diffView[i].initEditor();
            }
        },
        getEditors : function() {
            var editors = [];
            for(var i = 0; i < this.$refs.diffView.length; i++)
            {
                editors.push(this.$refs.diffView[i].getEditor());
            }
            return editors;
        },
        validate: function() {
            var correct = true;
            for(var i = 0; i < this.$refs.diffView.length; i++)
            {
                correct = this.$refs.diffView[i].validateEditor() && correct;
            }
            return correct;
        },
        getData: function() {
            var data = {};
            var hash = this.commit.revision_hash;
            for(var i = 0; i < this.$refs.diffView.length; i++)
            {
                data = Object.assign({}, data, this.$refs.diffView[i].getData(hash));
            }
            return data;
        }
    }
}
</script>
