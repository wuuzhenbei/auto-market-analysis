<template>
  <el-container class="app-container">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <h2>🚗 汽车分析</h2>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        class="sidebar-menu"
        background-color="#001529"
        text-color="#ffffffa6"
        active-text-color="#1890ff"
      >
        <el-menu-item index="/">
          <span>📊 市场总览</span>
        </el-menu-item>
        <el-menu-item index="/brands">
          <span>🏭 品牌分析</span>
        </el-menu-item>
        <el-menu-item index="/price">
          <span>💰 价格分析</span>
        </el-menu-item>
        <el-menu-item index="/energy">
          <span>⚡ 新能源分析</span>
        </el-menu-item>
        <el-menu-item index="/ratings">
          <span>⭐ 口碑分析</span>
        </el-menu-item>
        <el-menu-item index="/trends">
          <span>📈 趋势分析</span>
        </el-menu-item>
        <el-menu-item index="/cities">
          <span>🗺️ 城市分析</span>
        </el-menu-item>
      </el-menu>

      <!-- 导入按钮 -->
      <div class="import-section">
        <el-button type="primary" @click="showImportDialog = true" style="width: 100%">
          📥 导入数据
        </el-button>
      </div>
    </el-aside>

    <el-container>
      <el-header class="header">
        <h1>汽车市场数据分析平台</h1>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>

    <!-- 导入对话框 -->
    <el-dialog v-model="showImportDialog" title="📥 从懂车帝导入数据" width="500px">
      <div v-if="!importTaskId">
        <p>点击"开始导入"后，浏览器会自动打开懂车帝销量页面。</p>
        <p><strong>请在弹出的浏览器中手动登录</strong>（扫码或账号密码），登录成功后系统会自动抓取数据。</p>
        <el-alert type="info" :closable="false" style="margin-top: 12px">
          导入过程中请不要关闭浏览器窗口。
        </el-alert>
      </div>

      <div v-else>
        <el-progress :percentage="importProgress" :status="importStatus" style="margin-bottom: 16px" />
        <p>{{ importMessage }}</p>
      </div>

      <template #footer>
        <el-button @click="showImportDialog = false">关闭</el-button>
        <el-button
          v-if="!importTaskId"
          type="primary"
          :loading="importLoading"
          @click="startImport"
        >
          开始导入
        </el-button>
        <el-button
          v-if="importStatus === 'success'"
          type="success"
          @click="refreshPage"
        >
          刷新页面查看新数据
        </el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const showImportDialog = ref(false)
const importLoading = ref(false)
const importTaskId = ref(null)
const importProgress = ref(0)
const importMessage = ref('')
const importStatus = ref('')

let pollTimer = null

async function startImport() {
  importLoading.value = true
  try {
    const resp = await axios.post('/api/import/dongchedi')
    importTaskId.value = resp.data.task_id
    importMessage.value = '正在启动浏览器...'
    importProgress.value = 0

    // 开始轮询进度
    pollTimer = setInterval(async () => {
      try {
        const statusResp = await axios.get(`/api/import/status/${importTaskId.value}`)
        const task = statusResp.data

        importProgress.value = task.progress || 0
        importMessage.value = task.message || ''

        if (task.status === 'done') {
          importStatus.value = 'success'
          clearInterval(pollTimer)
          ElMessage.success('数据导入完成！')
        } else if (task.status === 'error') {
          importStatus.value = 'exception'
          clearInterval(pollTimer)
          ElMessage.error('导入失败: ' + task.message)
        }
      } catch (e) {
        // 忽略轮询错误
      }
    }, 1000)
  } catch (e) {
    ElMessage.error('连接后端失败，请确保 FastAPI 已启动')
  } finally {
    importLoading.value = false
  }
}

function refreshPage() {
  window.location.reload()
}
</script>

<style scoped>
.app-container {
  height: 100vh;
}
.sidebar {
  background: #001529;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}
.logo {
  padding: 16px;
  text-align: center;
  color: white;
  border-bottom: 1px solid #ffffff1a;
}
.logo h2 {
  margin: 0;
  font-size: 18px;
}
.sidebar-menu {
  border-right: none;
  flex: 1;
}
.import-section {
  padding: 16px;
  border-top: 1px solid #ffffff1a;
}
.header {
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  padding: 0 24px;
}
.header h1 {
  margin: 0;
  font-size: 18px;
  color: #333;
}
.main-content {
  background: #f0f2f5;
  padding: 24px;
  overflow-y: auto;
}
</style>
