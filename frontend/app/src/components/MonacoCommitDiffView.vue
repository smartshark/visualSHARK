<template>
<div class="card" :id="commit.revision_hash">
<div class="card-header">
             <div v-on:click="scrollToCommit(commit)">
              <i class="fa fa-bug"></i> Commit <a :href="vcs_url + commit.revision_hash" target="_blank">{{commit.revision_hash}}</a>

              <button class="btn btn-primary" v-on:click="top()" style="float: right;">Jump to top</button>
              </div>
            </div>
            <div :id="'collapse' + commit.revision_hash">
            <div class="card-block">
<div class="row">
<label class="col-sm-2">Commit Message</label>
<div class="col-sm-10">
            <pre class="form-control">{{ commit.message }}</pre>
            </div>
            </div>
            <div v-for="c in commit.changes" :key="c.revision_hash">
                <MonacoDiffView :file="c" :lines="c.lines" ref="diffView" />
            </div>
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
    commit : Object,
    vcs_url : String,
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
            var correct = [];
            for(var i = 0; i < this.$refs.diffView.length; i++)
            {
                if(!this.$refs.diffView[i].validateEditor())
                {
                    correct.push(this.commit.changes[i]);
                }
            }
            return correct;
        },
        showValidation: function(show) {
            for(var i = 0; i < this.$refs.diffView.length; i++)
            {
                this.$refs.diffView[i].changeValidation(show);
            }
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
