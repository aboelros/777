import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import api from '../../../services/api';

export function useBotTrainingData(currentProject, activeTab) {
  const queryClient = useQueryClient();
  const projectId = currentProject?.id;

  // Instructions queries & mutations
  const { data: instructionsData, isLoading: isLoadingInstructions } = useQuery({
    queryKey: ['bot-instructions', projectId],
    queryFn: () => api.botTraining.getInstructions(projectId),
    enabled: !!projectId && activeTab === 'instructions',
  });
  const instructions = instructionsData?.instructions || [];

  const createInstructionMutation = useMutation({
    mutationFn: (data) => api.botTraining.createInstruction(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['bot-instructions']);
      toast.success('تمت إضافة التعليمات بنجاح!');
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'فشل في حفظ التعليمات'),
  });

  const updateInstructionMutation = useMutation({
    mutationFn: ({ id, data }) => api.botTraining.updateInstruction(projectId, id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['bot-instructions']);
      toast.success('تم تحديث التعليمات بنجاح!');
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'فشل في تعديل التعليمات'),
  });

  const deleteInstructionMutation = useMutation({
    mutationFn: (id) => api.botTraining.deleteInstruction(projectId, id),
    onSuccess: () => {
      queryClient.invalidateQueries(['bot-instructions']);
      toast.success('تم حذف التعليمات بنجاح!');
    },
    onError: () => toast.error('فشل في حذف التعليمات'),
  });

  const seedMutation = useMutation({
    mutationFn: () => api.botTraining.seedInstructions(projectId),
    onSuccess: (data) => {
      queryClient.invalidateQueries(['bot-instructions']);
      toast.success(data.message || 'تمت إضافة باقة تعليمات البائع البشري بنجاح!');
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'فشل في إضافة الباقة'),
  });

  // Knowledge queries & mutations
  const { data: knowledgeData, isLoading: isLoadingKnowledge } = useQuery({
    queryKey: ['knowledge-base', projectId],
    queryFn: () => api.knowledge.list(projectId),
    enabled: !!projectId && activeTab === 'knowledge',
  });
  const knowledgeItems = knowledgeData || [];

  const createKnowledgeMutation = useMutation({
    mutationFn: (data) => api.knowledge.create(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['knowledge-base']);
      toast.success('تمت إضافة عنصر المعرفة بنجاح!');
    },
    onError: () => toast.error('فشل في إضافة عنصر المعرفة'),
  });

  const updateKnowledgeMutation = useMutation({
    mutationFn: ({ id, data }) => api.knowledge.update(projectId, id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['knowledge-base']);
      toast.success('تم تحديث عنصر المعرفة بنجاح!');
    },
    onError: () => toast.error('فشل في تحديث عنصر المعرفة'),
  });

  const deleteKnowledgeMutation = useMutation({
    mutationFn: (id) => api.knowledge.delete(projectId, id),
    onSuccess: () => {
      queryClient.invalidateQueries(['knowledge-base']);
      toast.success('تم حذف عنصر المعرفة!');
    },
    onError: () => toast.error('فشل في حذف عنصر المعرفة'),
  });

  const scrapeMutation = useMutation({
    mutationFn: (url) => api.knowledge.scrape(projectId, { url }),
    onSuccess: () => {
      queryClient.invalidateQueries(['knowledge-base']);
      toast.success('تم سحب المحتوى بنجاح وإضافته لقاعدة المعرفة!');
    },
    onError: () => toast.error('فشل في سحب محتوى الرابط. يرجى النسخ اليدوي.'),
  });

  return {
    instructions,
    isLoadingInstructions,
    createInstructionMutation,
    updateInstructionMutation,
    deleteInstructionMutation,
    seedMutation,
    knowledgeItems,
    isLoadingKnowledge,
    createKnowledgeMutation,
    updateKnowledgeMutation,
    deleteKnowledgeMutation,
    scrapeMutation,
  };
}
