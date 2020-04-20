<template>
  <div class="sidebar">
    <nav class="sidebar-nav">
      <ul class="nav">
        <li class="nav-item">
          <router-link :to="'/dashboard'" class="nav-link"><i class="icon-speedometer"></i> Dashboard</router-link>
        </li>
        <li class="nav-item" v-if="permissions.includes('view_commits')">
          <router-link :to="'/commits'" class="nav-link"><i class="fa fa-code"></i> Commits</router-link>
        </li>
        <li class="nav-item" v-if="permissions.includes('view_issues')">
          <router-link :to="'/issues'" class="nav-link"><i class="fa fa-bug"></i> Issues</router-link>
        </li>
        <li class="nav-item" v-if="permissions.includes('view_files')">
          <router-link :to="'/files'" class="nav-link"><i class="fa fa-files-o"></i> Files</router-link>
        </li>
        <li class="nav-item" v-if="permissions.includes('view_messages')">
          <router-link :to="'/messages'" class="nav-link"><i class="fa fa-envelope"></i> Messages</router-link>
        </li>
        <li class="nav-item" v-if="permissions.includes('view_people')">
          <router-link :to="'/people'" class="nav-link"><i class="fa fa-group"></i> People</router-link>
        </li>
        <router-link tag="li" class="nav-item nav-dropdown" :to="{ path: '/labeling'}" disabled>
          <div class="nav-link nav-dropdown-toggle open" @click="handleClick"><i class="fa fa-tags"></i> Manual Labels</div>
            <ul class="nav-dropdown-items">
              <li class="nav-item" v-if="permissions.includes('view_issue_labels')">
                <router-link :to="'/labeling/issuetype'" class="nav-link"><i class="fa fa-bug"></i> Issue Types</router-link>
              </li>
              <li class="nav-item" v-if="permissions.includes('view_issue_conflicts')">
                <router-link :to="'/labeling/issuetypeconflicts'" class="nav-link"><i class="fa fa-check"></i> Issue Type Conflicts</router-link>
              </li>
              <li class="nav-item" v-if="permissions.includes('view_issue_links')">
                <router-link :to="'/labeling/commitissuelinks'" class="nav-link"><i class="fa fa-link"></i> Commit->Issue Links</router-link>
              </li>
              <li class="nav-item" v-if="permissions.includes('view_line_labels')">
                <router-link :to="'/labeling/lines'" class="nav-link"><i class="fa fa-file"></i> Changed Lines</router-link>
              </li>
              <li class="nav-item" v-if="permissions.includes('view_line_labels')">
                <router-link :to="'/labeling/linesOld'" class="nav-link"><i class="fa fa-file"></i> Changed Lines Old</router-link>
              </li>
              <li class="nav-item" v-if="permissions.includes('view_line_labels')">
                <router-link :to="'/labeling/leaderboard'" class="nav-link"><i class="fas fa-crown"></i> Leaderboard</router-link>
              </li>
            </ul>
        </router-link>
        <router-link tag="li" class="nav-item nav-dropdown" :to="{ path: '/analytics'}" disabled v-if="permissions.includes('view_analytics')">
          <div class="nav-link nav-dropdown-toggle" @click="handleClick"><i class="fa fa-bar-chart"></i> Analytics</div>
          <ul class="nav-dropdown-items">
            <li class="nav-item">
              <router-link :to="'/analytics/project'" class="nav-link" exact><i class="fa fa-info"></i> Project</router-link>
            </li>
            <li class="nav-item">
              <router-link :to="'/analytics/cgraph'" class="nav-link" exact><i class="fa fa-code"></i> Commit Graph</router-link>
            </li>
            <li class="nav-item">
              <router-link :to="'/analytics/issuelinklist'" class="nav-link" exact><i class="fa fa-link"></i> Defect Links</router-link>
            </li>
            <li class="nav-item">
              <router-link :to="'/analytics/productinformation'" class="nav-link" exact><i class="fa fa-tags"></i> Product Stats</router-link>
            </li>
            <li class="nav-item">
              <router-link :to="'/analytics/prediction'" class="nav-link" exact><i class="fa fa-line-chart"></i> Prediction</router-link>
            </li>
            <li class="nav-item">
              <router-link :to="'/analytics/release'" class="nav-link" exact><i class="fa fa-flag-checkered"></i> Release Finder</router-link>
            </li>
            <!--<li class="nav-item">
              <router-link :to="'/analytics/history'" class="nav-link" exact><i class="fa fa-history"></i> History</router-link>
            </li>-->
          </ul>
        </router-link>
        <router-link tag="li" class="nav-item nav-dropdown" :to="{ path: '/system'}" disabled v-if="isSuperuser">
          <div class="nav-link nav-dropdown-toggle" @click="handleClick"><i class="fa fa-cogs"></i> System</div>
          <ul class="nav-dropdown-items">
            <li class="nav-item">
              <router-link :to="'/system/jobs'" class="nav-link" exact><i class="fa fa-tasks"></i> Jobs</router-link>
            </li>
            <li class="nav-item">
              <router-link :to="'/system/info'" class="nav-link" exact><i class="fa fa-info"></i> Info</router-link>
            </li>
          </ul>
        </router-link>
        <li class="nav-item">
          <router-link :to="'/help'" class="nav-link"><i class="fa fa-question"></i> Help</router-link>
        </li>
      </ul>
    </nav>
  </div>
</template>
<script>
import { mapGetters } from 'vuex'

export default {
  name: 'sidebar',
  methods: {
    handleClick (e) {
      e.preventDefault()
      e.target.parentElement.classList.toggle('open')
    }
  },
  computed: mapGetters({
    isSuperuser: 'isSuperuser',
    permissions: 'permissions'
  })
}
</script>

<style lang="css">
  .nav-link {
    cursor:pointer;
  }
</style>
