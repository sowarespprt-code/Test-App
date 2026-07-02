<template>
  <div class="flex flex-col h-full">
    <div v-if="isLoading" class="flex items-center justify-center flex-col mt-20">
      <LoadingIndicator :scale="8" class="text-ink-gray-5" />
      <p class="text-xl font-medium text-ink-gray-5 mt-4">
        Loading Activities...
      </p>
    </div>
    <div v-else class="flex flex-col flex-1 overflow-y-auto mt-4 px-4">
      <div v-if="_activities.length" class="activities flex-1 h-full mt-1">
        <div
          v-for="(activity, i) in _activities"
          :key="activity.key"
          class="activity"
        >
          <div class="w-full px-2 md:px-6 grid grid-cols-[30px_minmax(auto,_1fr)] gap-2 sm:gap-4">
            <div class="relative flex justify-center after:absolute after:left-[50%] after:top-2 after:-z-10 after:border-l after:border-gray-200" :class="[i != _activities.length - 1 ? 'after:h-full' : 'after:h-4']">
              <div class="z-1 flex h-7 w-7 items-center justify-center rounded-full bg-white">
                <CommentIcon v-if="activity.type === 'comment'" class="text-gray-600 absolute left-[7.5px]" />
                <DotIcon v-else class="text-gray-600 absolute left-[7.5px]" />
              </div>
            </div>
            
            <div class="mb-4 flex flex-1" :class="[i == _activities.length - 1 && 'mb-5']">
              <div v-if="activity.type === 'comment'" class="w-full bg-gray-50 p-3 rounded-lg border border-gray-200 text-sm">
                <div class="flex justify-between text-gray-500 mb-1">
                  <span class="font-medium text-gray-900">{{ activity.commenter }}</span>
                  <span>{{ timeAgo(activity.creation) }}</span>
                </div>
                <div class="text-gray-800 break-words" v-html="activity.content"></div>
              </div>
              
              <div v-else-if="activity.type === 'history'" class="w-full py-1 text-sm text-gray-600">
                <span class="font-medium text-gray-900">{{ activity.user }}</span>
                <span>{{ activity.content }}</span>
                <span class="text-gray-400 ml-2 text-xs">{{ timeAgo(activity.creation) }}</span>
                
                <div v-if="activity.relatedActivities && activity.relatedActivities.length" class="mt-1">
                  <div v-for="rel in activity.relatedActivities" :key="rel.key" class="text-xs text-gray-500">
                    <span>{{ rel.content }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="h-40 flex flex-col items-center justify-center gap-3 text-xl font-medium text-gray-500">
        <ActivityIcon class="h-10 w-10 text-gray-400" />
        <span>No Activities Found</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { call, LoadingIndicator } from "frappe-ui";
import ActivityIcon from "~icons/lucide/activity";
import CommentIcon from "~icons/lucide/message-square";
import DotIcon from "~icons/lucide/circle";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";

dayjs.extend(relativeTime);

const props = defineProps({
  doctype: {
    type: String,
    required: true,
  },
  docname: {
    type: String,
    required: true,
  },
});

const isLoading = ref(true);
const activities = ref<any>({ comments: [], history: [], views: [] });

function timeAgo(dateString: string) {
  if (!dateString) return "";
  return dayjs(dateString).fromNow();
}

async function fetchActivities() {
  isLoading.value = true;
  try {
    const res = await call("test_app.api.timeline.get_task_activities", {
      doctype: props.doctype,
      docname: props.docname,
    });
    activities.value = res || { comments: [], history: [], views: [] };
  } catch (e) {
    console.error("Failed to fetch activities", e);
  } finally {
    isLoading.value = false;
  }
}

const _activities = computed(() => {
  if (!activities.value) return [];

  const commentProps = (activities.value.comments || []).map((comment: any) => {
    return {
      name: comment.name,
      type: "comment",
      key: comment.creation,
      commentedBy: comment.commented_by,
      commenter: comment.user?.name || comment.commented_by,
      creation: comment.creation,
      content: comment.content,
    };
  });

  const historyProps = [
    ...(activities.value.history || []),
    ...(activities.value.views || []),
  ].map((h: any) => {
    return {
      type: "history",
      key: h.creation,
      content: h.action ? h.action : "viewed this",
      creation: h.creation,
      user: h.user?.name || h.owner,
    };
  });

  const sorted = [...commentProps, ...historyProps].sort(
    (a, b) => new Date(a.creation).getTime() - new Date(b.creation).getTime()
  );

  const data: any[] = [];
  let i = 0;

  while (i < sorted.length) {
    const currentActivity = sorted[i];

    if (currentActivity.type === "history") {
      currentActivity.relatedActivities = [];
      for (let j = i + 1; j < sorted.length + 1; j++) {
        const nextActivity = sorted[j];

        if (
          nextActivity &&
          nextActivity.type === "history" &&
          nextActivity.user === currentActivity.user &&
          nextActivity.content !== "viewed this" &&
          currentActivity.content !== "viewed this" &&
          new Date(nextActivity.creation).getTime() - new Date(currentActivity.creation).getTime() < 5000 // Group if within 5 seconds
        ) {
          currentActivity.relatedActivities.push(nextActivity);
        } else {
          data.push(currentActivity);
          i = j - 1;
          break;
        }
      }
    } else {
      data.push(currentActivity);
    }
    i++;
  }

  return data;
});

onMounted(() => {
  if (props.doctype && props.docname) {
    fetchActivities();
  }
});

defineExpose({
  fetchActivities
});
</script>
