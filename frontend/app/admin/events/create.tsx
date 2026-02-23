import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../../../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import Constants from 'expo-constants';

const API_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL;

export default function CreateEventScreen() {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [date, setDate] = useState('');
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const { token } = useAuth();
  const router = useRouter();

  const handleCreate = async () => {
    if (!name || !description || !date || !location) {
      Alert.alert('Erro', 'Preencha todos os campos');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/events`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name,
          description,
          date,
          location,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Erro ao criar evento');
      }

      Alert.alert('Sucesso!', 'Evento criado com sucesso', [
        {
          text: 'OK',
          onPress: () => router.back(),
        },
      ]);
    } catch (error: any) {
      Alert.alert('Erro', error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Criar Evento</Text>
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.form}>
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Nome do Evento *</Text>
            <TextInput
              style={styles.input}
              placeholder="Ex: Festival de Música 2025"
              value={name}
              onChangeText={setName}
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Descrição *</Text>
            <TextInput
              style={[styles.input, styles.textArea]}
              placeholder="Descreva seu evento..."
              value={description}
              onChangeText={setDescription}
              multiline
              numberOfLines={4}
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Data e Hora *</Text>
            <TextInput
              style={styles.input}
              placeholder="2025-12-31T20:00:00"
              value={date}
              onChangeText={setDate}
            />
            <Text style={styles.hint}>Formato: AAAA-MM-DDTHH:MM:SS</Text>
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Local *</Text>
            <TextInput
              style={styles.input}
              placeholder="Ex: Parque Ibirapuera, São Paulo"
              value={location}
              onChangeText={setLocation}
            />
          </View>

          <View style={styles.infoCard}>
            <Ionicons name="information-circle" size={20} color="#6200ee" />
            <Text style={styles.infoText}>
              Após criar o evento, você poderá adicionar produtos no cardápio.
            </Text>
          </View>
        </View>
      </ScrollView>

      <View style={styles.footer}>
        <TouchableOpacity
          style={styles.cancelButton}
          onPress={() => router.back()}
        >
          <Text style={styles.cancelButtonText}>Cancelar</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.createButton, loading && styles.buttonDisabled]}
          onPress={handleCreate}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Ionicons name="checkmark" size={20} color="#fff" />
              <Text style={styles.createButtonText}>Criar Evento</Text>
            </>
          )}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
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
  content: {
    flex: 1,
  },
  form: {
    padding: 16,
  },
  inputGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    color: '#333',
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  hint: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  infoCard: {
    flexDirection: 'row',
    backgroundColor: '#f0e6ff',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    gap: 12,
    marginTop: 8,
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    color: '#6200ee',
  },
  footer: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  cancelButton: {
    flex: 1,
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#6200ee',
    alignItems: 'center',
    justifyContent: 'center',
  },
  cancelButtonText: {
    color: '#6200ee',
    fontSize: 16,
    fontWeight: 'bold',
  },
  createButton: {
    flex: 2,
    flexDirection: 'row',
    padding: 16,
    borderRadius: 12,
    backgroundColor: '#6200ee',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  createButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});