<script setup>
import { ref } from 'vue'
import {getData, postData} from "@/api/api.js";

const url = ref("")
const selectedReasons = ref([])
const reasons = [
  { value: 1, label: "Наименование закупки совпадает с наименованием в техническом задании и/или в проекте контракта" },
  { value: 2, label: "Обеспечение исполнения контракта - требуется" },
  { value: 3, label: "Наличие сертификатов/лицензий" },
  { value: 4, label: "График поставки И этап поставки" },
  { value: 5, label: "Максимальное значение цены контракта ИЛИ начальная цена" },
  { value: 6, label: "Спецификации" },
]

function isValidUrl(string) {
  const pattern = new RegExp('^(https?:\\/\\/)?' +
      '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|' +
      '((\\d{1,3}\\.){3}\\d{1,3}))' +
      '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*' +
      '(\\?[;&a-z\\d%_.~+=-]*)?' +
      '(\\#[-a-z\\d_]*)?$', 'i');
  return !!pattern.test(string);
}

const tasksShow = ref([])

const statusWorker = async (tasks) => {
  const tasksUnCompleted = ref([])

  Object.keys(tasks).forEach((task) => {
    tasksUnCompleted.value.push({
      id: task,
      url: tasks[task],
      status: "processing",
      result: {}
    })
  })

  tasksShow.value = tasksUnCompleted.value

  while (tasksUnCompleted.value.length > 0) {
    for (const task of tasksUnCompleted.value) {
      try {
        const response = await getData(`analyze/${task.id}`)
        const status = response.status
        const result = response.result

        if (status === "completed" || status === "failed") {
          const index = tasksShow.value.findIndex(t => t.id === task.id)
          if (index !== -1) {
            tasksShow.value[index].status = status
            tasksShow.value[index].result = status === "completed" ? result : {}
          }
          tasksUnCompleted.value = tasksUnCompleted.value.filter(t => t.id !== task.id)
        }
      } catch (error) {
        console.error(`Error processing task ${task.id}:`, error)
      }
    }

    // await new Promise(resolve => setTimeout(resolve, 1000))
  }
}

async function checkKS() {
  const urlsSend = url.value.split('\n').map(item => item.trim()).filter(Boolean);

  if (urlsSend.length === 0) {
    alert("Введите хотя бы один URL для проверки.");
    return;
  }

  const invalidUrls = urlsSend.filter(item => !isValidUrl(item));
  if (invalidUrls.length > 0) {
    alert(`Найдены некорректные URL:\n${invalidUrls.join('\n')}`);
    return;
  }

  if (selectedReasons.value.length === 0) {
    alert("Выберите хотя бы одно основание для проверки.");
    return;
  }
  const selectedLabels = selectedReasons.value
    .map(selected => reasons.find(reason => reason.value === selected)?.label)
    .map((label, index) => `${index + 1}. ${label}`);

  alert(`Проверка КС по URL:\n${urlsSend.join('\n')}\n\nВыбранные основания: \n${selectedLabels.join('\n')}`);

  const response = await postData("analyze", {urls: urlsSend, validate_params: selectedReasons.value})
  if (response) {
     await statusWorker(response.task_ids)
  } else {
    alert("Ошибка обработки ссылок КС")
  }

}
</script>

<template>
  <div class="container">
    <h2>Основания для снятия КС с публикации</h2>

    <label for="url">Введите URL (каждый с новой строки)</label>
    <textarea id="url" v-model="url" placeholder="Введите URL для проверки, каждый с новой строки..."></textarea>

    <div class="checkbox-group">
      <div v-for="reason in reasons" :key="reason.value" class="checkbox-item">
        <input
            type="checkbox"
            :value="reason.value"
            v-model="selectedReasons"
            :id="'reason-' + reason.value"
        />
        <label :for="'reason-' + reason.value">{{ reason.label }}</label>
      </div>
    </div>

    <button @click="checkKS">Проверить КС</button>

    <div v-if="tasksShow.length > 0" class="tasks-status">
      <h3>Статус обработки ссылок КС</h3>
      <ul>
        <li v-for="task in tasksShow" :key="task.id" class="task-item">
          <template v-if="task.status === 'processing'">
            {{ task.url }} <span class="loader"></span>
          </template>

          <template v-else-if="task.status === 'completed'">
            <details>
              <summary>
                <a :href="task.url" target="_blank" rel="noopener noreferrer">{{ task.url }}</a>
              </summary>
              <pre>{{ task.result }}</pre>
            </details>
          </template>

          <template v-else-if="task.status === 'failed'">
            {{ task.url }} <span class="failed">✖</span>
          </template>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

h2 {
  color: #333;
  font-size: 1.5em;
  margin-bottom: 20px;
  text-align: center;
}

label {
  display: block;
  font-size: 1em;
  color: #555;
  margin-bottom: 5px;
}

textarea {
  width: 100%;
  height: 100px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1em;
  resize: vertical;
  margin-bottom: 20px;
  transition: border-color 0.3s;
}

textarea:focus {
  border-color: #007bff;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.checkbox-item {
  display: flex;
  align-items: center;
}

input[type="checkbox"] {
  margin-right: 8px;
}

button {
  display: inline-block;
  width: 100%;
  padding: 10px;
  font-size: 1em;
  color: #fff;
  background-color: #007bff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #0056b3
}

button:active {
  background-color: #003d80;
}

.tasks-status ul {
  list-style-type: none;
  padding: 0;
}

.task-item {
  display: flex;
  align-items: center;
  border: 1px solid #ddd;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 5px;
  background-color: #f9f9f9;
  font-size: 0.9em;
}

.loader {
  border: 2px solid #f3f3f3;
  border-top: 2px solid #007bff;
  border-radius: 50%;
  width: 12px;
  height: 12px;
  animation: spin 1s linear infinite;
  margin-left: 8px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.failed {
  color: #f44336;
  font-weight: bold;
  margin-left: 8px;
}

details summary {
  cursor: pointer;
  color: #007bff;
}

details summary a {
  text-decoration: none;
  color: inherit;
}
</style>