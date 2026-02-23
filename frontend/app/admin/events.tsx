import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import Constants from 'expo-constants';

const API_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL;

interface Event {
  id: string;
  name: string;
  date: string;
  location: string;
  status: string;
}

export default function AdminEventsScreen() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const { token } = useAuth();
  const router = useRouter();

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      const response = await fetch(`${API_URL}/api/events`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await response.json();
      setEvents(data);
    } catch (error) {
      console.error('Erro ao buscar eventos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = (eventId: string) => {
    Alert.alert(
      'Confirmar',
      'Tem certeza que deseja deletar este evento?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Deletar',
          style: 'destructive',
          onPress: async () => {
            try {
              await fetch(`${API_URL}/api/events/${eventId}`, {
                method: 'DELETE',
                headers: {
                  Authorization: `Bearer ${token}`,
                },
              });
              fetchEvents();
              Alert.alert('Sucesso', 'Evento deletado com sucesso');
            } catch (error) {
              Alert.alert('Erro', 'Não foi possível deletar o evento');
            }
          },
        },
      ]
    );
  };

  const renderEvent = ({ item }: { item: Event }) => (
    <View style={styles.eventCard}>
      <View style={styles.eventInfo}>
        <Text style={styles.eventName}>{item.name}</Text>
        <Text style={styles.eventLocation}>{item.location}</Text>
        <Text style={styles.eventDate}>
          {new Date(item.date).toLocaleDateString('pt-BR')}
        </Text>
        <View style={[styles.statusBadge, { backgroundColor: item.status === 'active' ? '#4caf50' : '#999' }]}>
          <Text style={styles.statusText}>{item.status === 'active' ? 'Ativo' : 'Inativo'}</Text>
        </View>
      </View>
      <View style={styles.eventActions}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => router.push(`/admin/events/edit/${item.id}`)}
        >
          <Ionicons name="create" size={20} color="#6200ee" />
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => router.push(`/admin/events/products/${item.id}`)}
        >
          <Ionicons name="fast-food" size={20} color="#ff9800" />
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => handleDelete(item.id)}
        >
          <Ionicons name="trash" size={20} color="#f44336" />
        </TouchableOpacity>
      </View>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#6200ee" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Gerenciar Eventos</Text>
      </View>

      <FlatList
        data={events}
        renderItem={renderEvent}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="calendar-outline" size={64} color="#ccc" />
            <Text style={styles.emptyText}>Nenhum evento cadastrado</Text>
          </View>
        }
      />

      <TouchableOpacity
        style={styles.fab}
        onPress={() => router.push('/admin/events/create')}
      >
        <Ionicons name="add" size={32} color="#fff" />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#6200ee',
    padding: 16,
    paddingTop: 48,
  },
  backButton: {
    marginRight: 16,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  listContent: {
    padding: 16,
  },
  eventCard: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  eventInfo: {
    flex: 1,
  },
  eventName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  eventLocation: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  eventDate: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  statusBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  statusText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  eventActions: {
    justifyContent: 'space-around',
  },
  actionButton: {
    padding: 8,
  },
  emptyContainer: {
    alignItems: 'center',
    padding: 32,
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
    marginTop: 16,
  },
  fab: {
    position: 'absolute',
    right: 16,
    bottom: 16,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#6200ee',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
});