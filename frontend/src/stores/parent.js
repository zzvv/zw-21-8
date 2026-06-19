import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getChildren } from '../api/parent.js'

export const useParentStore = defineStore('parent', () => {
  const children = ref([])
  const selectedChildId = ref(null)

  const selectedChild = computed(() => {
    if (!selectedChildId.value) return null
    return children.value.find(c => c.id === selectedChildId.value)
  })

  async function loadChildren() {
    try {
      children.value = await getChildren()
      if (children.value.length > 0) {
        const saved = localStorage.getItem('selectedChild')
        if (saved && children.value.some(c => c.id === parseInt(saved))) {
          selectedChildId.value = parseInt(saved)
        } else {
          selectedChildId.value = children.value[0].id
          localStorage.setItem('selectedChild', selectedChildId.value)
        }
      }
    } catch (e) {
      console.error('加载孩子列表失败', e)
    }
  }

  function selectChild(id) {
    selectedChildId.value = id
    localStorage.setItem('selectedChild', id)
  }

  return { children, selectedChildId, selectedChild, loadChildren, selectChild }
})