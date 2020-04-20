<template>
  <aside class="aside-menu px-2">
    <div class="aside-options">
        <h6>Project</h6>
        <select v-model="currentProject" class="form-control">
            <option v-for="item in projects" :value="item">{{ item.name }}</option>
        </select>
        <br/>
        <h6>VCS</h6>
        <select v-model="currentVcs" class="form-control">
            <option v-for="item in vcs" :value="item">{{ item.url }}</option>
        </select>
        <br/>
        <h6>ITS</h6>
        <select v-model="currentIts" class="form-control">
            <option v-for="item in its" :value="item">{{ item.url }}</option>
        </select>
        <br/>
        <h6>ML</h6>
        <select v-model="currentMl" class="form-control">
            <option v-for="item in mls" :value="item">{{ item.name }}</option>
        </select>
    </div>
  </aside>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'rightside',
  computed: {
    ...mapGetters({
      projects: 'allProjects',
      vcs: 'projectsVcs',
      its: 'projectsIts',
      mls: 'projectsMls'
    }),
    currentProject: {
      get () {
        return this.$store.getters.currentProject
      },
      set (value) {
        this.$store.dispatch('setProject', value)
      }
    },
    currentVcs: {
      get () {
        return this.$store.getters.currentVcs
      },
      set (value) {
        this.$store.dispatch('setVcs', value)
      }
    },
    currentIts: {
      get () {
        return this.$store.getters.currentIts
      },
      set (value) {
        this.$store.dispatch('setIts', value)
      }
    },
    currentMl: {
      get () {
        return this.$store.getters.currentMl
      },
      set (value) {
        this.$store.dispatch('setMl', value)
      }
    }
  }
}
</script>

<style>
.aside-options {
    padding-top: 15px;
}
.aside-menu { /* defaults to 999???*/
  z-index: -1;
}
</style>
