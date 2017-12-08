<template>
  <div class="wrapper">
    <div class="animated fadeIn">
      <div class="card">
        <div class="card-header">
          Projects <button type="button" class="btn btn-primary float-right mt-0 btn-sm" @click="addProjectModal = true">add</button>
        </div>
        <div class="card-block">
          <grid :gridColumns="grid.columns" :data="grid.data" :count="grid.count" :defaultPerPage="5" defaultFilterField="title" @refresh="refreshProjectsGrid">
            <template slot="customer" scope="props">
              <td><router-link :to="{ name: 'Customer', params: { id: props.object.id }}">{{ props.object.short_name }} ({{ props.object.id }})</router-link></td>
            </template>
          </grid>
        </div>
      </div>
    </div>

    <modal title="Add Project" :show="addProjectModal" @ok="addProjectModal = false" @close="addProjectModal = false">
      <div slot="title">
        Add Project
      </div>
      <div slot="modal-body" class="modal-body">
        <form method="POST" enctype="application/json" @submit="createProject">
          <vue-form-generator :schema="project.schema" :model="project.model" :formOptions="project.formOptions"></vue-form-generator>
        </form>
      </div>
      <!--<div slot="modal-footer" class="modal-footer">
      buttons
      </div>-->
    </modal>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

import rest from '../api/rest'

import Grid from '@/components/Grid.vue'
import modal from '@/components/Modal'

export default {
  name: 'projects',
  data () {
    return {
      grid: {
        columns: [
          {ident: 'customer', sortIdent: 'customer__short_name', filterIdent: 'customer__short_name', name: 'Kunde'},
          {ident: 'title', sortIdent: 'title', filterIdent: 'title', name: 'Projekt'},
          {ident: 'planned_hours', name: 'Stunden geplant'}
        ],
        data: [],
        count: 0
      },
      addProjectModal: false,
      addCustomerModal: false,
      customers: [],
      project: {
        model: {
          customers: ''
        },
        schema: {
          fields: [{
            type: 'input',
            inputType: 'text',
            label: 'Name',
            required: true
          },
          {
            type: 'fieldSelect',
            label: 'Kunde',
            model: 'customers',
            options: [],
            placeholder: 'Suche Kunden',
            labelKey: 'short_name',
            values (search, loading) {
              // this is the only way we can get the call for select2 back, this in this context is the schema.field
              loading(true)
              let dat = {'search': search}
              rest.getCustomers(dat)
              .then(response => {
                if (typeof response.data.results === 'undefined') {
                  this.options = response.data
                } else {
                  this.options = response.data.results
                }
                loading(false)
              })
              .catch(e => {
                // somehow show an error without this
                // we could create an extra schema attribute for this
                loading(false)
              })
            },
            required: true
          },
          {
            type: 'submit',
            buttonText: 'ok',
            validateBeforeSubmit: true,
            onSubmit () {
              console.log('submitted!')
            }
          }]
        },
        formOptions: {
          validateAfterChanged: true,
          validateAfterLoad: true
        }
      }
    }
  },
  components: {
    Grid, modal
  },
  methods: {
    createProject (ev) {
      // there is probabyl a shortcut in vuejs for this
      ev.preventDefault()
      this.addProjectModal = false
      console.log(this.project.model)
      console.log(ev)
    },
    refreshProjectsGrid (dat) {
      this.$Progress.start()
      rest.getProjects(dat)
      .then(response => {
        this.$Progress.finish()
        if (typeof response.data.results === 'undefined') {
          this.grid.data = response.data
          this.grid.count = response.data.length
        } else {
          this.grid.data = response.data.results
          this.grid.count = response.data.count
        }
      })
      .catch(e => {
        this.grid.data = []
        this.grid.count = 0
        this.$Progress.fail()
      })
    }
  },
  computed: mapGetters({
    customers: 'allCustomers',
    error: 'error',
    error_msg: 'error_msg'
  })
}
</script>
