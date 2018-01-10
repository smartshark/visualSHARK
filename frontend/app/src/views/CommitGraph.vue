<template>
  <div class="wrapper">
    <div class="animated fadeIn" v-if="currentProject && currentVcs">
      <div class="row">
        <div class="col-sm-12">
          <div class="card">
            <div class="card-header">
              <i class="fa fa-code"></i> Commit Graph for {{currentProject.name}}
              <div class="card-actions">
                <dropdown class="inline" v-model="showDownload">
                  <span slot="button">
                    <i class="fa fa-cloud-download"></i>
                  </span>
                  <div slot="dropdown-menu"class="dropdown-menu dropdown-menu-right">
                    <div class="dropdown-header text-center"><strong>Download Graph</strong></div>
                      <a id="fillGraph" v-text="dlText"></a>
                  </div>
                </dropdown>
                <dropdown class="inline">
                  <span slot="button">
                    <i class="fa fa-plus"></i>
                  </span>
                  <div slot="dropdown-menu"class="dropdown-menu dropdown-menu-right">
                    <div class="dropdown-header text-center"><strong>Add Release</strong></div>
                  </div>
                </dropdown>
                <dropdown class="inline">
                  <span slot="button">
                    <i class="fa fa-search"></i>
                  </span>
                  <div slot="dropdown-menu"class="dropdown-menu dropdown-menu-right">
                    <div class="dropdown-header text-center"><strong>Search Commits</strong></div>
                    <div class="input-group" style="width: 600px">
                      <span class="input-group-addon">Message</span>
                      <input type="text" v-model="searchMessageDebounce" class="form-control">
                    </div>
                  </div>
                </dropdown>
                <dropdown class="inline">
                  <span slot="button">
                    <i class="fa fa-random"></i>
                  </span>
                  <div slot="dropdown-menu"class="dropdown-menu dropdown-menu-right">
                    <div class="dropdown-header text-center"><strong>Find Path</strong></div>
                    <ul class="path-dropdown">
                      <li>
                        <a href="javascript:void(0)" @click="startPath">
                          <template v-if="startCommit">{{ startCommit.revisionHash }}</template>
                          <template v-else>start</template>
                        </a>
                      </li>
                      <li>
                        <a href="javascript:void(0)" @click="endPath">
                          <template v-if="endCommit">{{ endCommit.revisionHash }}</template>
                          <template v-else>end</template>
                        </a>
                      </li>
                    </ul>
                  </div>
                </dropdown>
                <dropdown>
                  <span slot="button">
                    <i class="fa fa-eye"></i>
                  </span>
                  <div slot="dropdown-menu" class="dropdown-menu dropdown-menu-right">
                    <div class="dropdown-header text-center"><strong>View Options</strong></div>
                    <div class="input-group" style="width: 600px">
                      <span class="input-group-addon">Radius {{ nodeRadiusDebounce }}</span>
                      <input type="range" v-model.number="nodeRadiusDebounce" min="0.1" max="10" step="0.1" class="form-control">
                    </div>
                    <div class="input-group" style="width: 600px">
                      <span class="input-group-addon">Minimum {{ filesCommittedDebounce}} Files Committed</span>
                      <input type="range" v-model.number="filesCommittedDebounce" min="0" max="100" class="form-control">
                    </div>
                    <div class="input-group">
                      <input type="checkbox" v-model="graphOptions.showDirection" class="checkbox-dropdown">
                      <div class="checkbox-label">Show Direction</div>
                    </div>
                    <div class="input-group">
                      <input type="checkbox" v-model="showArticulationPoints" class="checkbox-dropdown">
                      <div class="checkbox-label">Show articulation points</div>
                    </div>
                    <div class="input-group" style="width: 600px">
                      <input type="checkbox" v-model="showCommitLabel" class="checkbox-dropdown">
                      <div class="checkbox-label" style="width: 220px;">Show commit label</div>
                      <multiselect v-model="currentCommitLabelFields" :options="commitLabelFields" :multiple="true" track-by="id" label="label"></multiselect>
                        <!--<select v-model="currentCommitLabelField" class="form-control">
                          <option v-for="item in commitLabelFields" :value="item.id">{{item.approach }}: {{ item.name }}</option>
                        </select>-->
                    </div>
                    <div class="input-group" style="width: 600px">
                      <input type="checkbox" v-model="showProduct" class="checkbox-dropdown">
                      <div class="checkbox-label" style="width: 220px;">Show Product</div>
                      <multiselect v-model="currentProducts" :options="products.data" :multiple="true" track-by="id" label="name"></multiselect>
                        <!--<select v-model="currentProduct" class="form-control">
                          <option v-for="item in products.data" :value="item.id">{{ item.name }}</option>
                        </select>-->
                    </div>
                    <div class="input-group" style="width: 600px">
                      <input type="checkbox" v-model="showTravisStates" class="checkbox-dropdown">
                      <div class="checkbox-label" style="width: 220px;">Travis States</div>
                      <multiselect v-model="currentTravisStates" :options="travisStates" :multiple="true"></multiselect>
                    </div>
                    <div class="input-group">
                      <input type="checkbox" v-model="graphOptions.onlyTags" class="checkbox-dropdown">
                      <div class="checkbox-label">Only Tags</div>
                    </div>
                    <div class="input-group">
                      <input type="checkbox" v-model="graphOptions.onlyCodeFiles" class="checkbox-dropdown">
                      <div class="checkbox-label">Only Code Files</div>
                    </div>
                  </div>
                </dropdown>
              </div>
            </div>
            <div class="card-block" style="overflow: scroll" @mousemove.prevent="dragster" @mousedown.prevent="resetOffsets" @wheel.prevent="zoom" id="svg-container">
              <svg width="100%" height="600" id="svg-graph" v-if="currentCommitGraph.directed_graph">
                <Graph :nodes="currentCommitGraph.directed_graph.nodes" :edges="currentCommitGraph.directed_graph.edges" :minX="currentCommitGraph.directed_graph.min_x" :maxX="currentCommitGraph.directed_graph.max_x" :minY="currentCommitGraph.directed_graph.min_y" :maxY="currentCommitGraph.directed_graph.max_y" :scaleFactor="scaleFactor" :nodeRadius="nodeRadius" :options="graphOptions" @hoverNode="hoverNode" @clickNode="clickNode" :possiblePaths="possiblePaths" :productPaths="productPaths" :showBugFixing="showBugFixing" :bugFixingNodes="bugFixingNodes" :markNodes="markNodes" :articulationPoints="articulationPoints"></Graph>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="animated fadeIn" v-if="currentProject && !currentVcs">
      <alert type="danger" dismissable>
        <span class="icon-info-circled alert-icon-float-left"></span>
        <strong>No VCS</strong>
        <p>
          No VCS set for Project {{ currentProject.name }}
        </p>
      </alert>
    </div>
    <div class="animated fadeIn" v-if="!currentProject">
      <alert type="danger" dismissable>
        <span class="icon-info-circled alert-icon-float-left"></span>
        <strong>No Project Selected</strong>
        <p>
          Select a Project first
        </p>
      </alert>
    </div>

    <div class="commitView" v-if="showCommit && currentCommit.revision_hash">
      <div class="card">
        <div class="card-header">
          <router-link :to="{ name: 'Commit', params: { id: currentCommit.revision_hash }}">{{ currentCommit.revision_hash }}</router-link>
        </div>
        <div class="card-block">
          {{ currentCommit.committer_date }}<br/>
          {{ currentCommit.message }}<br/>
          <span v-if="currentCommit.tags.length > 0">Tags:<br/></span>
          <ul v-if="currentCommit.tags.length > 0">
            <li v-for="tag in currentCommit.tags">{{ tag.name }}</li>
          </ul>
          <span v-if="currentCommit.labels.length > 0"><br/>Labels: </span>
          <template v-for="label in currentCommit.labels">{{ label.name }} : {{ label.value }}&nbsp;</template>
          <span v-if="currentCommit.issue_links.length > 0"><br/>Issue links: </span>
          <template v-for="il in currentCommit.issue_links"><router-link :to="{ name: 'Issue', params: { id: il.id }}">{{ il.name }}</router-link>&nbsp;</template>
          <br/>
          {{ currentCommit.branches }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { alert, dropdown, checkbox } from 'vue-strap'
import { debounce } from 'lodash'

import Multiselect from 'vue-multiselect'
import Graph from '@/components/Graph'

export default {
  name: 'analytics',
  props: {id: false},
  data () {
    return {
      scaleFactor: 1000,
      wheelScroll: 1,
      showDownload: false,
      nodeRadius: 5,
      nodeRadiusDebounce: 5,
      filesCommittedDebounce: 0,
      showCommit: false,
      showGraph: true,
      graphOptions: {onlyTags: false, onlyNumberFilesCommitted: 0, onlyCodeFiles: false, offsetX: 10, offsetY: 10, showDirection: false},
      offsets: {x: 0, y: 0},
      matrix: [1, 0, 0, 1, 0, 0],
      width: 0,
      height: 0,
      startCommit: false,
      endCommit: false,
      startPathCommit: false,
      endPathCommit: false,
      showProduct: false,
      currentReleaseApproach: 1,
      showBugFixing: false,
      showArticulationPoints: false,
      currentDefectLinkApproach: 1,
      searchMessageDebounce: '',
      searchMessage: '',
      dlText: 'loading...',
      showCommitLabel: false,
      cgConfig: {vcsId: null, searchMessage: null, label: null, travis: null},
      currentCommitLabelFields: [],
      currentCommitLabelField: 0,
      currentProduct: 0,
      currentProducts: [],
      showTravisStates: false,
      currentTravisStates: [],
      // todo: this needs to be in global state requested from backend
      travisStates: ['PASSED', 'FAILED', 'ERROR']
    }
  },
  components: {
    alert, Graph, dropdown, checkbox, Multiselect
  },
  computed: mapGetters({
    currentProject: 'currentProject',
    currentVcs: 'currentVcs',
    currentCommitGraph: 'currentCommitGraph',
    currentCommit: 'currentCommit',
    possiblePaths: 'possiblePaths',
    possiblePathsReleases: 'possiblePathsReleases',
    releaseApproaches: 'releaseApproaches',
    defectLinkApproaches: 'defectLinkApproaches',
    commitLabelFields: 'commitLabelFields',
    bugFixingNodes: 'bugFixingNodes',
    markNodes: 'markNodes',
    articulationPoints: 'articulationPoints',
    products: 'products',
    productPaths: 'productPaths'
  }),
  mounted () {
    // TODO: add to basic data (same as projects)
    this.$store.dispatch('getProducts', {'filter': '&vcs_system_id=' + this.currentVcs.id, order: 'name'})
    this.$store.dispatch('getCommitLabelFields', {})
    this.$store.dispatch('getCommitGraph', this.currentVcs.id)
    this.cgConfig.vcsId = this.currentVcs.id
  },
  watch: {
    currentCommitLabelFields (value) {
      console.log(value)
      console.log(value.map(a => a.id))
    },
    showDownload (value) {
      // this is the simplest method available to save the svg by embedding all of it into the download attribute of the a tag.
      // this will not scale to big graphs
      // TODO: rebuild this to server side job, fetch the resulting file like in ProductInformation.vue
      if (value === true) {
        const svgStyles = `
  <defs>
    <style type="text/css">
      <![CDATA[
      ]]>
    </style>
  </defs>
`
        const svgHeader = `
<?xml version="1.0" standalone="no"?>

<?xml-stylesheet href="style.css" type="text/css"?>

<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" xmlns="http://www.w3.org/2000/svg">
        `

        const svgFooter = `
</svg>
        `
        let a = document.getElementById('fillGraph')
        let g = document.getElementById('svg-graph')
        a.setAttributeNS(null, 'href-lang', 'image/svg+xml')
        a.setAttributeNS(null, 'href', 'data:image/svg+xml;utf8,' + svgHeader + svgStyles + g.innerHTML + svgFooter)
        a.setAttributeNS(null, 'download', this.currentProject.name + '_commitgaph.svg')
        a.setAttributeNS(null, 'target', '_blank')
        this.dlText = 'Save SVG'
      }
    },
    currentVcs (value) {
      if (typeof value.id !== 'undefined') {
        this.$store.dispatch('getProducts', {'filter': '&vcs_system_id=' + value.id, order: 'name'})
        this.$store.dispatch('getCommitGraph', value.id)
        this.cgConfig.vcsId = value.id

        this.showGraph = true
        this.nodeRadius = 5
        this.searchMessageDebounce = ''
        this.nodeRadiusDebounce = 5
        this.filesCommittedDebounce = 0
        this.showReleases = false
        this.showBugFixing = false
        this.startCommit = false
        this.endCommit = false
        this.graphOptions = {onlyTags: false, onlyNumberFilesCommitted: 0, onlyCodeFiles: false, offsetX: 10, offsetY: 10, showDirection: false, showBugFixing: false}
        let tmp = 'matrix(' + this.matrix.join(' ') + ')'
        document.getElementById('cg-elements').setAttributeNS(null, 'transform', tmp)
        this.dlText = 'loading...'
      }
    },
    showArticulationPoints (value) {
      if (value === true) {
        this.$store.dispatch('getArticulationPoints', {commitGraph: this.currentVcs.id})
      } else if (value === false) {
        this.$store.dispatch('clearArticulationPoints')
      }
    },
    currentProducts (value) {
      if (this.showProduct === true) {
        this.$store.dispatch('getProductPaths', {commitGraph: this.currentVcs.id, productIds: this.currentProducts.map(a => a.id)})
      }
    },
    showProduct (value) {
      if (value === true && this.currentProducts.length > 0) {
        this.$store.dispatch('getProductPaths', {commitGraph: this.currentVcs.id, productIds: this.currentProducts.map(a => a.id)})
      } else {
        this.$store.dispatch('clearProductPaths')
      }
    },
    showBugFixing (value) {
      if (value === true) {
        this.$store.dispatch('getBugFixingNodes', {commitGraph: this.currentVcs.id, approach: this.currentDefectLinkApproach})
      } else if (value === false) {
        this.$store.dispatch('clearBugFixingNodes')
      }
    },
    currentDefectLinkApproach (value) {
      if (this.graph.showBugFixing === true) {
        this.$store.dispatch('getDefectLinks', {commitGraph: this.currentVcs.id, approach: this.currentDefectLinkApproach})
      }
    },
    nodeRadiusDebounce (value) {
      this.debounceInputRadius(value)
    },
    filesCommittedDebounce (value) {
      this.debounceInputFilesCommitted(value)
    },
    searchMessageDebounce (value) {
      this.debounceInputSearchMessage(value)
    },
    currentCommitLabelField (value) {
      if (this.showCommitLabel === true) {
        this.cgConfig.label = this.currentCommitLabelFields.map(a => a.id)
        // this.cgConfig.label = currentCommitLabelFields.find(item => item.id === countryCode);
      }
      this.$store.dispatch('getMarkNodes', this.cgConfig)
    },
    searchMessage (value) {
      // todo: change this to mutate cgConfig in store
      if (value !== '') {
        this.cgConfig.searchMessage = value
      } else {
        this.cgConfig.searchMessage = null
      }
      this.$store.dispatch('getMarkNodes', this.cgConfig)
    },
    showCommitLabel (value) {
      if (value === true && this.currentCommitLabelFields.length > 0) {
        this.cgConfig.label = this.currentCommitLabelFields.map(a => a.id)
      } else {
        this.cgConfig.label = null
      }
      this.$store.dispatch('getMarkNodes', this.cgConfig)
    },
    showTravisStates (value) {
      console.log(this.currentTravisStates)
      if (value === true && this.currentTravisStates.length > 0) {
        this.cgConfig.travis = this.currentTravisStates
      } else {
        this.cgConfig.travis = null
      }
      this.$store.dispatch('getMarkNodes', this.cgConfig)
    }
  },
  methods: {
    debounceInputRadius: debounce(function () {
      this.nodeRadius = this.nodeRadiusDebounce
    }, 500),
    debounceInputSearchMessage: debounce(function () {
      this.searchMessage = this.searchMessageDebounce
    }, 500),
    debounceInputFilesCommitted: debounce(function () {
      this.graphOptions.onlyNumberFilesCommitted = this.filesCommittedDebounce
    }, 500),
    hoverNode (node) {
      this.showCommit = true
      this.$store.dispatch('getCommit', node.revisionHash)
    },
    clickNode (node) {
      if (this.startPathCommit === true) {
        this.startCommit = node
        this.startPathCommit = false
      }
      if (this.endPathCommit === true) {
        this.endCommit = node
        this.endPathCommit = false
      }

      if (this.startCommit !== false && this.endCommit !== false) {
        this.$store.dispatch('getPossiblePaths', {commitGraph: this.currentVcs.id, startCommit: this.startCommit.revisionHash, endCommit: this.endCommit.revisionHash})
      }
      // console.log('path: ', this.startCommit, this.endCommit)
    },
    startPath () {
      this.startPathCommit = true
    },
    endPath () {
      this.endPathCommit = true
    },
    dragster (e) {
      this.oldX = e.offsetX
      this.oldY = e.offsetY
      if (e.buttons === 1) {
        let diffY = (e.offsetY - this.offsets.y)
        let diffX = (e.offsetX - this.offsets.x)
        this.matrix[4] = this.offsets.offX + diffX
        this.matrix[5] = this.offsets.offY + diffY
        this.transform()
      } else {
        this.offsets = {x: e.offsetX, y: e.offsetY, offX: this.matrix[4], offY: this.matrix[5]}
      }
    },
    transform () {
      // reset svg transforms
      let textMatrix = 'matrix(' + this.matrix.join(' ') + ')'
      document.getElementById('cg-elements').setAttributeNS(null, 'transform', textMatrix)
    },
    resetOffsets (e) {
      this.showCommit = false
    },
    zoom (e) {
      let rect = document.getElementById('svg-graph').getBoundingClientRect()
      this.width = rect.width
      this.height = rect.height
      this.showCommit = false
      if (e.deltaY < 0) {
        this.wheelScroll = 1.1
      } else {
        this.wheelScroll = 0.9
      }

      for (let i = 0; i < this.matrix.length; i++) {
        this.matrix[i] *= this.wheelScroll
      }
      this.matrix[4] += (1 - this.wheelScroll) * this.width / 2
      this.matrix[5] += (1 - this.wheelScroll) * this.height / 2

      this.transform()
    }
  }
}
</script>

<style>
@import '~vue-multiselect/dist/vue-multiselect.min.css';

.commitView {
  position: absolute;
  top: -10px;
  left: 0;
  right: 0;
  margin: 0 auto;
  width: 700px;
  height: 100px;
}

#svg-graph {
  transform: matrix(1 0 0 1 0 0);
  min-width: 100%;
  overflow: visible; /* chrome need this otherwise it will cut off everything outside the view box */
}

#cg-elements {
  transform: matrix(1 0 0 1 0 0);
}

.checkbox-dropdown {
  height: 2rem;
  margin-right: 0.5rem;
  margin-left: 0.1rem;
}

.checkbox-label {
  line-height: 1.8rem;
}

.path-dropdown {
  list-style: none;
  clear: both;
  margin: 0px;
  padding: 0px;
  width: 600px;
  border: 0px;
}

.path-dropdown li {
  clear: both;
  border: 0px;
  margin-left: 15px;
}

#fillGraph {
  width: 100%;
}

.btn-override {
  width: auto !important;
  padding: 0.5rem 1rem !important;
  border: 1px solid transparent !important;
  border-color: #20a8d8 !important;
  background-color: #20a8d8 !important;
  color: white !important;
}

.btn-override:hover {
  background-color: #2192ba !important;
}
</style>
