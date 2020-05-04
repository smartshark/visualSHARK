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
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(0, 0, 0, 0.3);
  display: flex;
  justify-content: center;
  align-items: center;
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
    background: #FFFFFF;
    box-shadow: 2px 2px 20px 1px;
    overflow-x: auto;
    display: flex;
    flex-direction: column;
}

.modal-header,
.modal-footer {
  padding: 15px;
  display: flex;
}

.modal-header {
  border-bottom: 1px solid #eeeeee;
  color: #4AAE9B;
  justify-content: space-between;
}

.modal-footer {
  border-top: 1px solid #eeeeee;
  justify-content: flex-end;
}

.modal-body {
  position: relative;
  padding: 20px 10px;
}

</style>
