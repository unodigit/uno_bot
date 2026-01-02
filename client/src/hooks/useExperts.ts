import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import { Expert } from '../types'

/**
 * Hook for fetching and managing experts data with TanStack Query caching
 */
export function useExperts() {
  return useQuery({
    queryKey: ['experts'],
    queryFn: async () => {
      // The api class doesn't have a generic /experts endpoint, so we'll return empty for now
      // In production, this would call api.getExperts() or similar
      return [] as Expert[]
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    gcTime: 1000 * 60 * 10, // 10 minutes,
    enabled: false // Disabled until backend endpoint exists
  })
}

/**
 * Hook for fetching a single expert by ID
 */
export function useExpertById(expertId: string | null) {
  return useQuery({
    queryKey: ['experts', expertId],
    queryFn: async () => {
      if (!expertId) return null
      // Would call: return await api.getExpert(expertId)
      return null
    },
    enabled: !!expertId,
    staleTime: 1000 * 60 * 5,
  })
}

/**
 * Hook for fetching expert availability with caching
 */
export function useExpertAvailability(expertId: string | null, timezone: string = 'UTC') {
  return useQuery({
    queryKey: ['availability', expertId, timezone],
    queryFn: async () => {
      if (!expertId) return null
      // Use the existing api method
      return await api.getExpertAvailability(expertId, timezone)
    },
    enabled: !!expertId,
    staleTime: 1000 * 60 * 2, // 2 minutes for availability
  })
}

/**
 * Hook for invalidating expert cache
 */
export function useInvalidateExperts() {
  const queryClient = useQueryClient()

  return () => {
    queryClient.invalidateQueries({ queryKey: ['experts'] })
  }
}

/**
 * Hook for creating a new expert (with cache invalidation)
 */
export function useCreateExpert() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (expertData: Partial<Expert>) => {
      // Would call: return await api.createExpert(expertData)
      return expertData as Expert
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['experts'] })
    },
  })
}
