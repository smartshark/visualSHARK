<template>
  <div class="wrapper">
    <div class="animated fadeIn">
      <div class="card">
        <div class="card-header">
          <i class="fa fa-info"></i> Current Project {{ currentProject.name }}
        </div>
        <div class="card-block">
          <div class="row">
            <div class="col-sm-6 col-md-4 col-lg-4">
              <strong>Version Control Systems</strong><br/>
              <template v-for="p in projectsVcs">
                {{ p.url }}<br/><span class="updated">{{ p.last_updated|momentgerman }}</span><br/>
              </template>
            </div>
            <div class="col-sm-6 col-md-4 col-lg-4">
              <strong>Issue Tracking Systems</strong><br/>
              <template v-for="p in projectsIts">
                {{ p.url }}<br/><span class="updated">{{ p.last_updated|momentgerman }}</span><br/>
              </template>
            </div>
            <div class="col-sm-6 col-md-4 col-lg-4">
              <strong>Mailing Lists</strong><br/>
              <template v-for="p in projectsMl">
                {{ p.url }}<br/><span class="updated">{{ p.last_updated|momentgerman }}</span><br/>
              </template>
            </div>
          </div>
        </div>
      </div>       
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'project',
  data () {
    return {
    }
  },
  components: {
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
.updated {
    font-size: 0.7rem;
    opacity: 0.6;
}
.updated:before {
    content: "last update ";
}
</style>
