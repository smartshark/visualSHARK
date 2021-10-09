<template>
  <div>
    <form id="search" v-if="filterFields.length > 0">
      <div class="row">
        <div class="col-sm-6">
          <div class="input-group">
            <span class="input-group-addon">Filter</span>
            <select v-model="filterField" class="form-control">
              <option v-for="item in filterFields" v-bind:value="item.filterIdent">{{item.name}}</option>
            </select>
            <input name="query" v-model="filterString" class="form-control" placeholder="exact match">
          </div>
        </div>
        <div class="col-sm-6">
          <div class="input-group">
            <span class="input-group-addon">Search</span>
            <input name="search" v-model="searchString" class="form-control" placeholder="partial match">
          </div>
        </div>
      </div>
    </form>
    <br/>
    <table :class="{table: true, tloading: loading}">
      <thead>
        <tr>
          <template v-for="item in gridColumns">
          <th v-if="sortFields.indexOf(item) !== -1"
            @click="sortBy(item.sortIdent)"
            :class="{ active: sortKey == item.sortIdent, sortable: true }">
            {{ item.name }}
            <span class="arrow" :class="sortClass[item.sortIdent]">
            </span>
          </th>
          <th v-else>
            {{ item.name }}
          </th>
          </template>
        </tr>
      </thead>
      <tfoot>
        <tr>
          <td :colspan="gridColumns.length">
            <div class="input-group" style="width: 150px">
              <select v-model="perPage" class="form-control">
                <option value="5">5</option>
                <option value="15">15</option>
                <option value="30">30</option>
                <option value="50">50</option>
              </select>
              <span class="input-group-addon">per Page</span>
            </div>
            {{ count }} objects on {{ numPages }} pages     
          </td>
        </tr>
      </tfoot>
      <tbody>
        <tr v-for="entry in data">
          <slot :name="item.ident" :object="entry[item.ident]" :row="entry" v-for="item in gridColumns">
            <td>{{entry[item.ident]}}</td>
          </slot>
        </tr>
      </tbody>
    </table>
    <!--<button v-on:click="prev" v-if="currentPage > 0">prev</button>-->
    <nav aria-label="Page navigation">
      <ul v-if="pages" class="pagination">
        <li v-for="page in pages" :class="{ active: page - 1 == currentPage }"><a href="javascript:void(0)" @click="setPage(page)">{{page}}</a></li>
      </ul>
    </nav>
    <!--<button v-on:click="next" v-if="currentPage < pages.length - 1">next</button>-->
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  props: {
    data: [Array, Object],
    filterKey: String,
    defaultPerPage: Number,
    defaultFilterField: String,
    defaultOrder: [Array, Object],
    count: Number,
    gridColumns: [Array, Object],
    triggerRefresh: Boolean
  },
  data () {
    let sortOrders = {}
    let sortClass = {}
    this.gridColumns.forEach(item => {
      // only some columns are sortable
      if (typeof item.sortIdent !== 'undefined') {
        sortOrders[item.sortIdent] = 0
        sortClass[item.sortIdent] = ''
      }
    })

    // default orders shusld be possible, we override here
    if (typeof this.defaultOrder !== 'undefined') {
      sortOrders[this.defaultOrder.field] = this.defaultOrder.type
      if (this.defaultOrder.type === -1) {
        sortClass[this.defaultOrder.field] = 'dsc'
      } else if (this.defaultOrder.type === 1) {
        sortClass[this.defaultOrder.field] = 'asc'
      }
    }

    // set default filter field, if it is not defined set the first of existing
    let ff = this.defaultFilterField
    if (typeof ff === 'undefined' && typeof this.filterFields !== 'undefined' && this.filterFields.length > 0) {
      ff = this.filterFields[0].ident
    }
    return {
      sortKey: '',
      sortOrders: sortOrders,
      currentPage: 0,
      filterString: '',
      filterField: ff,
      perPage: Number(this.defaultPerPage),
      searchString: '',
      sortClass: sortClass
    }
  },
  created () {
    this.refresh()
  },
  computed: {
    ...mapGetters({
      loading: 'loading'
    }),
    offset () {
      return this.currentPage * this.perPage
    },
    filterFields () {
      let ff = []
      this.gridColumns.forEach(item => { if (typeof item.filterIdent !== 'undefined') { ff.push(item) } })
      return ff
    },
    sortFields () {
      let sf = []
      this.gridColumns.forEach(item => { if (typeof item.sortIdent !== 'undefined') { sf.push(item) } })
      return sf
    },
    // not really portable
    order () {
      let order = []
      for (let k in this.sortOrders) {
        if (this.sortOrders[k] === -1) {
          order.push('-' + k)
        }
        if (this.sortOrders[k] === 1) {
          order.push('' + k)
        }
      }
      return order
    },
    // not really portable
    filter () {
      if (this.filterString !== '') {
        return '&' + this.filterField + '=' + this.filterString
      } else {
        return ''
      }
    },
    search () {
      return this.searchString
    },
    numPages () {
      return Math.ceil(this.count / this.perPage)
    },
    pages () {
      let numPages = this.numPages

      let pages = []
      if (numPages > 10) {
        let start = this.currentPage - 5
        let end = this.currentPage + 5
        if (start < 0) {
          start = 1
          end = end + 5
        }
        if (end > this.numPages) {
          end = this.numPages
        }
        for (let i = start; i <= end; i++) {
          pages.push(i)
        }
      } else {
        for (let i = 1; i <= numPages; i++) {
          pages.push(i)
        }
      }
      return pages
    }
  },
  watch: {
    // add debounce here
    filterString (value) {
      // clear filter
      if (value.length === 0) {
        this.refresh()
      }

      // this does not work if we support lengths < 3
      if (value.length > 2) {
        this.currentPage = 0
        this.refresh()
      }
    },
    // add debounce here
    searchString (value) {
      // clear filter
      if (value.length === 0) {
        this.refresh()
      }

      // this does not work if we support lengths < 3
      if (value.length > 2) {
        this.currentPage = 0
        this.refresh()
      }
    },
    perPage () {
      this.currentPage = 0
      this.refresh()
    },
    triggerRefresh (value) {
      if (value === true) {
        this.refresh()
      }
    }
  },
  methods: {
    sortBy (key) {
      this.sortKey = key
      if (this.sortOrders[key] === 0) {
        this.sortOrders[key] = 1
        this.sortClass[key] = 'asc'
      } else if (this.sortOrders[key] === 1) {
        this.sortOrders[key] = -1
        this.sortClass[key] = 'dsc'
      } else if (this.sortOrders[key] === -1) {
        this.sortOrders[key] = 0
        this.sortClass[key] = ''
      }
      this.refresh()
    },
    refresh () {
      this.localLoading = true
      let dat = {'limit': Number(this.perPage), 'offset': this.offset, 'filter': this.filter, 'order': this.order.join(), 'search': this.search}
      this.$emit('refresh', dat)
    },
    setPage (page) {
      this.currentPage = page - 1
      this.refresh()
    },
    next () {
      this.currentPage += 1
      this.refresh()
    },
    prev () {
      this.currentPage -= 1
      this.refresh()
    }
  }
}
</script>

<style>
table.tloading {
  opacity: 0.3;
}

th.sortable {
  cursor: pointer;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}
th, td {
  min-width: 120px;
  padding: 10px 20px;
}

th.active {
}

th.active .arrow {
  opacity: 1;
}

.arrow {
  display: inline-block;
  vertical-align: middle;
  width: 0;
  height: 0;
  margin-left: 5px;
  opacity: 0.66;
}

.arrow.asc {
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-bottom: 4px solid #000;
}

.arrow.dsc {
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 4px solid #000;
}
</style>
