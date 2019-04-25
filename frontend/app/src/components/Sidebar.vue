<template>
  <div class="sidebar">
    <nav class="sidebar-nav">
      <ul class="nav">
        <li class="nav-item">
          <router-link :to="'/dashboard'" class="nav-link"><i class="icon-speedometer"></i> Dashboard</router-link>
        </li>
        <li class="nav-item">
          <router-link :to="'/commits'" class="nav-link"><i class="fa fa-code"></i> Commits</router-link>
        </li>
        <li class="nav-item">
          <router-link :to="'/issues'" class="nav-link"><i class="fa fa-bug"></i> Issues</router-link>
        </li>
        <li class="nav-item">
          <router-link :to="'/files'" class="nav-link"><i class="fa fa-files-o"></i> Files</router-link>
        </li>
        <li class="nav-item">
          <router-link :to="'/messages'" class="nav-link"><i class="fa fa-envelope"></i> Messages</router-link>
        </li>
        <li class="nav-item">
          <router-link :to="'/people'" class="nav-link"><i class="fa fa-group"></i> People</router-link>
        </li>
        <router-link tag="li" class="nav-item nav-dropdown" :to="{ path: '/analytics'}" disabled>
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
        <router-link tag="li" class="nav-item nav-dropdown" :to="{ path: '/system'}" disabled>
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
      </ul>
    </nav>
  </div>
</template>
<script>

export default {
  name: 'sidebar',
  methods: {
    handleClick (e) {
      e.preventDefault()
      e.target.parentElement.classList.toggle('open')
    }
  }
}
</script>

<style lang="css">
  .nav-link {
    cursor:pointer;
  }
</style>
