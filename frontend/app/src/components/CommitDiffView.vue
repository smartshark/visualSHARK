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
                <DiffView :file="c" ref="diffView" />
            </template>
            </div>
            </div>
            </div>
</template>
<script>

import DiffView from '@/components/DiffView.vue'

export default {
    components: {
        DiffView
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
            for(var i = 0; i < this.$refs.diffView.length; i++)
            {
                this.$refs.diffView[i].validateEditor();
            }
        }
    }
}
</script>
