<template>
  <g>
    <g id="cg-legend"></g>
    <g id="cg-elements">
      <marker id="arrow" markerWidth="11" markerHeight="11" refX="-4" refY="6" orient="auto">
        <path d="M2,2 L2,11 L10,6 L2,2" style="fill: #000000;" />
      </marker>
      <line v-for="item in edges" :x1="item.x1" :y1="item.y1" :x2="item.x2" :y2="item.y2" :class="{edge: true, showDirection: options.showDirection, markEdge: myMarkPath.indexOf(item.key1) !== -1 || myMarkPath.indexOf(item.key2) !== -1}" :style="{strokeWidth: nodeRadius/10, stroke: releaseColor(item.key2)}"></line>
      <circle v-for="(n, k) in myNodes" :cx="n.x" :cy="n.y" :r="nodeRadius" @mouseover="hovernode(k)" @click="clicknode(k)" @mouseout="outnode(k)" :class="{bugFixing: bugFixingNodes.indexOf(k) !== -1 && showBugFixing, commit: true, markCommit2: articulationPoints.indexOf(k) !== -1}" :style="{fill: productColors[k], strokeWidth: nodeRadius, stroke: markColor(k)}"></circle>
    </g>
  </g>
</template>

<script>
export default {
  name: 'graph',
  props: {nodes: [Object], edges: [Array], maxX: Number, maxY: Number, minY: Number, minX: Number, scaleFactor: Number, nodeRadius: Number, options: [Object], possiblePaths: [Array, Object], productPaths: [Object, Array], showBugFixing: Boolean, bugFixingNodes: [Array], markNodes: [Object, Array], articulationPoints: [Array]},
  data () {
    return {
      productColors: {}
    }
  },
  methods: {
    hovernode (revisionHash) {
      this.$emit('hoverNode', {revisionHash})
    },
    outnode (revisionHash) {
      this.$emit('outNode', {revisionHash})
    },
    clicknode (revisionHash) {
      this.$emit('clickNode', {revisionHash})
    },
    scaleX (x) {
      let n = (x - this.minX) / (this.maxX - this.minX)
      return n * this.scaleFactor + parseFloat(this.options.offsetX)
    },
    scaleY (y) {
      let n = (y - this.minY) / (this.maxY - this.minY)
      return n * (this.scaleFactor / 4 * 3) + parseFloat(this.options.offsetY)
    },
    color (seed) {
      let col = '#' + Math.floor((Math.abs(Math.sin(seed) * 16777215)) % 16777215).toString(16)
      if (col.length < 7) {
        col = col + '0'
      }
      return col
    },
    rainbow (numOfSteps, step) {
      let r, g, b
      let h = step / numOfSteps
      let i = ~~(h * 6)
      let f = h * 6 - i
      let q = 1 - f
      switch (i % 6) {
        case 0: r = 1; g = f; b = 0; break
        case 1: r = q; g = 1; b = 0; break
        case 2: r = 0; g = 1; b = f; break
        case 3: r = 0; g = q; b = 1; break
        case 4: r = f; g = 0; b = 1; break
        case 5: r = 1; g = 0; b = q; break
      }
      let c = '#' + ('00' + (~~(r * 255)).toString(16)).slice(-2) + ('00' + (~~(g * 255)).toString(16)).slice(-2) + ('00' + (~~(b * 255)).toString(16)).slice(-2)
      return (c)
    },
    markColor (revisionHash) {
      if (this.markNodes.hasOwnProperty(revisionHash)) {
        const conv = this.markNodes[revisionHash].join(' & ')
        let s = ''
        for (let i = 0; i < conv.length; i++) {
          s = s + conv.charCodeAt(i)
        }
        // const col = this.color(s)
        // duplicate code with legend
        let labels = []
        for (let att in this.markNodes) {
          if (this.markNodes.hasOwnProperty(att)) {
            let conv = this.markNodes[att].join(' & ')
            if (labels.indexOf(conv) === -1) {
              labels.push(conv)
            }
          }
        }
        const col = this.rainbow(labels.length, labels.indexOf(conv))
        return col
      }
    },
    drawLegend () {
      let g = document.getElementById('cg-legend')
      let x = 0
      let y = 2
      let offw = 0
      if (typeof this.productPaths.paths !== 'undefined') {
        for (let i = 0; i < this.productPaths.products.length; i++) {
          x = offw
          let tmp = this.productPaths.products[i].lastIndexOf('-') + 1
          let labeltext = this.productPaths.products[i].substr(tmp)
          let col = this.color(this.getNumbers(labeltext))

          let circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
          circle.setAttributeNS(null, 'r', 5)
          circle.setAttributeNS(null, 'fill', col)
          circle.setAttributeNS(null, 'cx', x)
          circle.setAttributeNS(null, 'cy', y - 5)
          g.appendChild(circle)

          let label = document.createElementNS('http://www.w3.org/2000/svg', 'text')
          label.setAttributeNS(null, 'x', x + 10)
          label.setAttributeNS(null, 'y', y)

          let text = document.createTextNode(labeltext)
          label.appendChild(text)
          g.appendChild(label)

          offw = offw + labeltext.length * 8 + 15
        }
      }

      if (typeof this.possiblePaths.paths !== 'undefined') {
        for (let i = 0; i < this.possiblePaths.paths.length; i++) {
          x = offw
          let labeltext = 'path nr. ' + i
          let col = this.rainbow(this.possiblePaths.paths.length, i)

          let circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
          circle.setAttributeNS(null, 'r', 5)
          circle.setAttributeNS(null, 'fill', col)
          circle.setAttributeNS(null, 'cx', x)
          circle.setAttributeNS(null, 'cy', y - 5)
          g.appendChild(circle)

          let label = document.createElementNS('http://www.w3.org/2000/svg', 'text')
          label.setAttributeNS(null, 'x', x + 10)
          label.setAttributeNS(null, 'y', y)

          let text = document.createTextNode(labeltext)
          label.appendChild(text)
          g.appendChild(label)

          offw = offw + labeltext.length * 8 + 15
        }
      }

      // find unique combinations for legend
      let labels = []
      for (let att in this.markNodes) {
        if (this.markNodes.hasOwnProperty(att)) {
          let conv = this.markNodes[att].join(' & ')
          if (labels.indexOf(conv) === -1) {
            labels.push(conv)
          }
        }
      }

      // add labels to legend
      let i = 0
      for (let lbl in labels) {
        const labeltext = labels[lbl]
        // numeric representation for color seed
        // let col = this.color(this.getNumbers(labeltext))
        let col = this.rainbow(labels.length, i)
        i++
        x = offw
        let circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
        circle.setAttributeNS(null, 'r', 5)
        circle.setAttributeNS(null, 'fill', col)
        circle.setAttributeNS(null, 'cx', x)
        circle.setAttributeNS(null, 'cy', y - 5)
        circle.setAttributeNS(null, 'id', 'circle-' + labeltext)
        g.appendChild(circle)

        let label = document.createElementNS('http://www.w3.org/2000/svg', 'text')
        label.setAttributeNS(null, 'x', x + 10)
        label.setAttributeNS(null, 'y', y)

        let text = document.createTextNode(labeltext)
        label.appendChild(text)
        g.appendChild(label)

        offw = offw + labeltext.length * 8 + 10
      }
    },
    getNumbers (text) {
      let s = ''
      for (let i = 0; i < text.length; i++) {
        s = s + text.charCodeAt(i)
      }
      return s
    },
    removeLegend () {
      let g = document.getElementById('cg-legend')
      while (g.firstChild) {
        g.removeChild(g.firstChild)
      }
    },
    releaseColor (k) {
      if (this.productColors.hasOwnProperty(k)) {
        return this.productColors[k]
      }
    },
    createProductColors () {
      if (typeof this.productPaths.paths === 'undefined') {
        return
      }

      // determine the path in which the node resides, create the color and push to the object
      let i = 0
      for (let path of this.productPaths.paths) {
        let tmp = this.productPaths.products[i].lastIndexOf('-') + 1
        let labeltext = this.productPaths.products[i].substr(tmp)
        let col = this.color(this.getNumbers(labeltext))
        for (let node of path) {
          this.productColors[node] = col
        }
        i++
      }
    },
    createPathColors () {
      if (typeof this.possiblePaths.paths === 'undefined') {
        return
      }

      // determine the path in which the node resides, create the color and push to the object
      let i = 0
      for (let path of this.possiblePaths.paths) {
        // let labeltext = 'path nr. ' + i
        let col = this.rainbow(this.possiblePaths.paths.length, i)
        for (let node of path) {
          this.productColors[node] = col
        }
        i++
      }
    }
  },
  watch: {
    productPaths (value) {
      this.productColors = {}
      this.createProductColors()
      this.removeLegend()
      this.drawLegend()
    },
    markNodes (value) {
      this.removeLegend()
      this.drawLegend()
    },
    possiblePaths (value) {
      this.productColors = {}
      console.log('create possible paths', value)
      this.createPathColors()
      this.removeLegend()
      this.drawLegend()
    }
  },
  computed: {
    myMarkPath () {
      if (typeof this.possiblePaths.paths === 'undefined') {
        return []
      }

      let myMarkNodes = []
      for (let path of this.possiblePaths.paths) {
        for (let node of path) {
          if (myMarkNodes.indexOf(node) !== -1) {
            myMarkNodes.push(node)
          }
        }
      }
      return myMarkNodes
    },
    myNodes () {
      let newNodes = {}
      Object.keys(this.nodes).forEach(key => {
        if (this.options.onlyNumberFilesCommitted >= 0) {
          if (this.nodes[key].files_committed >= this.options.onlyNumberFilesCommitted) {
            newNodes[key] = this.nodes[key]
          }
        }
        if (this.options.onlyTags) {
          if (this.nodes[key].is_tag === true) {
            newNodes[key] = this.nodes[key]
          } else {
            delete newNodes[key]
          }
        }
        if (this.options.onlyCodeFiles) {
          if (this.nodes[key].java_files_committed > 0) {
            newNodes[key] = this.nodes[key]
          } else {
            delete newNodes[key]
          }
        }
      })
      return newNodes
    }
  }
}
</script>

<style>
line.edge {
  stroke: #5ece85;
}

line.showDirection {
  marker-start: url(#arrow);
}

line.markEdge {
  stroke: blue;
}

circle.commit {
  fill: #4dbd74;
}

circle.bugFixing {
  stroke: red;
  stroke-width: 0.1px;
}

circle.markCommit {
  stroke: blue;
  stroke-width: 0.1px;
}

circle.bugFixing.markCommit {
  stroke: magenta;
  stroke-width: 0.1px;
}

circle.markCommit2 {
  stroke: green;
  stroke-width: 0.1px;
}

circle.markCommit3 {
  stroke: black;
  stroke-width: 0.1px;
}

circle.commit:hover {
  opacity: 0.5;
}
</style>
