<template>
  <v-select
    v-model="value" 
    type="select2"
    :debounce="250"
    :on-search="getOptions"
    :options="schema.options"
    :disabled="disabled"
    :maxlength="schema.max"
    :readonly="schema.readonly"
    :placeholder="schema.placeholder"
    :label="schema.labelKey">
  </v-select>
</template>

<script>
  // here we wrap vue-select in a vue-form-generator compatible way
  import { abstractField } from 'vue-form-generator'
  import vSelect from 'vue-select'
  export default {
    props: {
      placeholder: String,
      label: String,
      options: [Array, Object]
    },
    mixins: [ abstractField ],
    components: {vSelect},
    methods: {
      getOptions (search, loading) {
        this.schema.values(search, loading)
      }
    }
  }
</script>
