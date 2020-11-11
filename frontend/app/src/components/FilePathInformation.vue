<template>
  <div>
    <i v-if="release" class="fa fa-home" style="float:left; line-height: 1.4rem; cursor: pointer" @click.prevent="currentPath = ''"></i>
    <ul class="fpi-breadcrumps">
      <li v-if="p !== ''" v-for="(p, index) in pathLinks" @click.prevent="clickcrump(index)" style="cursor: pointer">{{ p }}</li>
    </ul>
    <svg width="100%" height="400" id="fpi-svg" @mousemove.prevent="dragster" @wheel.prevent="zoom">
      <g id="fpi-legend"></g>
      <g id="fpi-elements">
        <template v-for="(n, k) in paths">
          <circle :cx="n.x" :cy="n.y" :r="n.files" @click.prevent="clicknode(k)" :fill="buggyness(n)" class="fpi-dir"><title :id="k">Files: {{ n.files }} / Bugs: {{ n.bugs }}<template v-if="n.labels">{{n.labels}}</template></title></circle>
          <text :x="n.x" :y="n.y - 1" text-anchor="middle" :font-size="n.files" class="fpi-label">{{ k }}<title>{{ k }}</title></text>
        </template>
      </g>
    </svg>
  </div>
</template>

<script>
export default {
  name: 'FilePathInformation',
  props: {release: [Array], options: [Object]},
  data () {
    return {
      currentPath: '',
      offsets: {x: 0, y: 0},
      matrix: [1, 0, 0, 1, 0, 0]
    }
  },
  watch: {
    release () {
      // reset all of this if we switch to another release
      this.currentPath = ''
      this.offsets = {x: 0, y: 0}
      this.matrix = [1, 0, 0, 1, 0, 0]
      this.transform()
    }
  },
  methods: {
    transform () {
      // reset svg transforms
      let textMatrix = 'matrix(' + this.matrix.join(' ') + ')'
      document.getElementById('fpi-elements').setAttributeNS(null, 'transform', textMatrix)
    },
    clickcrump (index) {
      // here we have to reset the release to trigger the computation of the graph, and after that restore the zoom and stuff
      let t = this.pathLinks.slice(0, index + 1)
      let tmp = this.release
      let tmpMatrix = this.matrix
      this.release = null
      this.release = tmp
      this.$nextTick(() => {
        this.currentPath = t.join('/') + '/'
        this.matrix = tmpMatrix
        this.transform()
      })
    },
    clicknode (path) {
      if (path.endsWith('.java')) {
        return
      }
      this.currentPath = this.currentPath + path + '/'
    },
    dragster (e) {
      // if we press the mouse button we transform, if not we save the data to know the starting point for the transform
      if (e.buttons === 1) {
        this.matrix[4] = this.offsets.offX + (e.offsetX - this.offsets.x)
        this.matrix[5] = this.offsets.offY + (e.offsetY - this.offsets.y)
        this.transform()
      } else {
        // set old values, we include x and y from the transformation here because the old values have to stay constant while dragging
        this.offsets = {x: e.offsetX, y: e.offsetY, offX: this.matrix[4], offY: this.matrix[5]}
      }
    },
    zoom (e) {
      // center and scroll
      let rect = document.getElementById('fpi-svg').getBoundingClientRect()
      let z = 0
      if (e.deltaY < 0) {
        z = 1.1
      } else {
        z = 0.9
      }
      for (let i = 0; i < this.matrix.length; i++) {
        this.matrix[i] *= z
      }
      this.matrix[4] += (1 - z) * rect.width / 2
      this.matrix[5] += (1 - z) * rect.height / 2
      this.transform()
    },
    buggyness (node) {
      let val = node.bugratio
      if (val > 100) {
        val = 100
      } else if (val < 0) {
        val = 0
      }

      let h = Math.floor((100 - val) * 120 / 100)
      let s = Math.abs(val - 50) / 50
      let v = 1

      return this.hsv2rgb(h, s, v)
    },
    hsv2rgb (h, s, v) {
      let rgb = []
      let i = []
      let data = []
      if (s === 0) {
        rgb = [v, v, v]
      } else {
        h = h / 60
        i = Math.floor(h)
        data = [v * (1 - s), v * (1 - s * (h - i)), v * (1 - s * (1 - (h - i)))]
        switch (i) {
          case 0:
            rgb = [v, data[2], data[0]]
            break
          case 1:
            rgb = [data[1], v, data[0]]
            break
          case 2:
            rgb = [data[0], v, data[2]]
            break
          case 3:
            rgb = [data[0], data[1], v]
            break
          case 4:
            rgb = [data[2], data[0], v]
            break
          default:
            rgb = [v, data[0], data[1]]
            break
        }
      }
      return '#' + rgb.map(function (x) {
        return ('0' + Math.round(x * 255).toString(16)).slice(-2)
      }).join('')
    }
  },
  computed: {
    pathLinks () {
      return this.currentPath.split('/')
    },
    paths () {
      let newPaths = {}
      if (typeof this.release === 'undefined') {
        return newPaths
      }

      if (this.release === null) {
        return newPaths
      }

      let rect = document.getElementById('fpi-svg').getBoundingClientRect()
      let centre = {x: rect.width / 2, y: rect.height / 2}
      let num = 0
      let biggestBugs = 0
      this.release.forEach((row) => {
        // do we match our current path
        if (row.file.startsWith(this.currentPath)) {
          // remove the current prefix
          let tmp = row.file.replace(this.currentPath, '')

          // split the path of the file
          tmp = tmp.split('/')
          if (newPaths[tmp[0]]) {
            newPaths[tmp[0]].files += 1
            newPaths[tmp[0]].bugs += row.bugs
          } else {
            newPaths[tmp[0]] = {files: 1, bugs: row.bugs}
            num += 1
          }

          if (row.bugs > biggestBugs) {
            biggestBugs = row.bugs
          }
        }
      })

      let ratio = biggestBugs / 100

      // everything around the centre of the biggest with the distance of the biggest
      let biggest = 0
      let biggestKey = null
      Object.keys(newPaths).forEach(key => {
        if (newPaths[key].files > biggest) {
          biggest = newPaths[key].files
          biggestKey = key
        }
      })

      newPaths[biggestKey].x = centre.x
      newPaths[biggestKey].y = centre.y
      let r = newPaths[biggestKey].files + 15
      // now fix positions?
      let i = 0
      Object.keys(newPaths).forEach(key => {
        if (key !== biggestKey) {
          newPaths[key].x = centre.x + ((r + newPaths[key].files) * Math.cos(2 * i * Math.PI / num))
          newPaths[key].y = centre.y + ((r + newPaths[key].files) * Math.sin(2 * i * Math.PI / num))
        }

        // apply bug ratio
        newPaths[key].bugratio = Math.floor(newPaths[key].bugs / ratio)
        i += 1
      })
      return newPaths
    }
  }
}
</script>

<style>
ul.fpi-breadcrumps {
  list-style-type: none;
  padding-left: 15px;
}

ul.fpi-breadcrumps li {
  float: left;
}
ul.fpi-breadcrumps li:after {
  content: "/";
}

.fpi-label {
  cursor: default;
  user-select: none;
}

.fpi-dir {
  cursor: pointer;
  stroke: grey;
  stroke-width: 0.1;
}
</style>
