<template>
  <div role="dialog" class="modal-mask" v-show="showModal" @click="close" transition="modal" style="display: block">
    <div class="modal-dialog in" role="document" @click.stop :style="{maxWidth: optionalWidth}">
      <div class="modal-content" :style="{width: optionalWidth}">
        <slot name="modal-header">
          <div class="modal-header">
            <h4 class="modal-title">
              <slot name="title">
              </slot>
            </h4>
            <button type="button" class="close" @click="close"><span>&times;</span></button>
          </div>
        </slot>
        <slot name="modal-body">
          <div class="modal-body"></div>
        </slot>
        <slot name="modal-footer">
        </slot>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  props: {
    show: false,
    width: null
  },
  computed: {
    showModal () {
      return this.show
    },
    optionalWidth () {
      console.log(this.width)
      if (this.width === null) {
        return null
      } else if (Number.isInteger(this.width)) {
        return this.width + 'px'
      }
      return this.width
    }
  },
  methods: {
    close () {
      this.$emit('close')
    }
  }
}
</script>
<style>
.modal-mask {
  position: fixed;
  z-index: 9998;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, .5);
  display: table;
  transition: opacity .3s ease;
}

.modal-enter, .modal-leave {
    opacity: 0;
}

.modal-enter .modal-dialog,
.modal-leave .modal-dialog {
    -webkit-transform: scale(1.1);
    transform: scale(1.1);
}

.modal-dialog {
  margin-top: 60px;
  max-width: none;
  max-height: 100%;
  overflow-y: scroll;
  overflow-x: hidden;
  max-height: 90%;
}
</style>
