import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import Constants from 'expo-constants';
import QRCode from 'react-native-qrcode-svg';

const API_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL;

interface Order {
  id: string;
  event_name: string;
  items: Array<{
    product_name: string;
    quantity: number;
    unit_price: number;
  }>;
  subtotal: number;
  platform_fee: number;
  credits_used: number;
  total: number;
  status: string;
  qr_code: string;
  created_at: string;
}

export default function OrderDetailScreen() {
  const { id } = useLocalSearchParams();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const { token } = useAuth();
  const router = useRouter();

  useEffect(() => {
    fetchOrder();
  }, [id]);

  const fetchOrder = async () => {
    try {
      const response = await fetch(`${API_URL}/api/orders/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Erro ao buscar pedido');
      }

      setOrder(data);
    } catch (error: any) {
      Alert.alert('Erro', error.message);
      router.back();
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'validated':
        return '#4caf50';
      case 'pending':
        return '#ff9800';
      case 'cancelled':
        return '#f44336';
      default:
        return '#999';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'validated':
        return 'Validado';
      case 'pending':
        return 'Pendente';
      case 'cancelled':
        return 'Cancelado';
      default:
        return status;
    }
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#6200ee" />
      </View>
    );
  }

  if (!order) {
    return (
      <View style={styles.centerContainer}>
        <Text>Pedido não encontrado</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Detalhes do Pedido</Text>
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.statusCard}>
          <View style={[styles.statusBadge, { backgroundColor: getStatusColor(order.status) }]}>
            <Ionicons
              name={order.status === 'validated' ? 'checkmark-circle' : 'time'}
              size={24}
              color="#fff"
            />
            <Text style={styles.statusText}>{getStatusText(order.status)}</Text>
          </View>
          {order.status === 'pending' && (
            <Text style={styles.statusDescription}>
              Apresente o QR Code no balcão para validar seu pedido
            </Text>
          )}
          {order.status === 'validated' && (
            <Text style={styles.statusDescription}>
              Seu pedido foi validado e entregue!
            </Text>
          )}
        </View>

        <View style={styles.qrSection}>
          <View style={styles.qrContainer}>
            <QRCode value={order.qr_code} size={200} />
          </View>
          <Text style={styles.qrCode}>{order.qr_code}</Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Evento</Text>
          <View style={styles.infoCard}>
            <Text style={styles.eventName}>{order.event_name}</Text>
            <View style={styles.infoRow}>
              <Ionicons name="calendar" size={16} color="#666" />
              <Text style={styles.infoText}>
                {new Date(order.created_at).toLocaleDateString('pt-BR')} às{' '}
                {new Date(order.created_at).toLocaleTimeString('pt-BR', {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </Text>
            </View>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Itens do Pedido</Text>
          <View style={styles.itemsCard}>
            {order.items.map((item, index) => (
              <View key={index} style={styles.orderItem}>
                <Text style={styles.itemName}>
                  {item.quantity}x {item.product_name}
                </Text>
                <Text style={styles.itemPrice}>
                  R$ {(item.unit_price * item.quantity).toFixed(2)}
                </Text>
              </View>
            ))}
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Resumo do Pagamento</Text>
          <View style={styles.summaryCard}>
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Subtotal</Text>
              <Text style={styles.summaryValue}>R$ {order.subtotal.toFixed(2)}</Text>
            </View>
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Taxa da plataforma (10%)</Text>
              <Text style={styles.summaryValue}>R$ {order.platform_fee.toFixed(2)}</Text>
            </View>
            {order.credits_used > 0 && (
              <View style={styles.summaryRow}>
                <Text style={[styles.summaryLabel, { color: '#4caf50' }]}>Créditos usados</Text>
                <Text style={[styles.summaryValue, { color: '#4caf50' }]}>
                  - R$ {order.credits_used.toFixed(2)}
                </Text>
              </View>
            )}
            <View style={[styles.summaryRow, styles.totalRow]}>
              <Text style={styles.totalLabel}>Total pago</Text>
              <Text style={styles.totalValue}>R$ {order.total.toFixed(2)}</Text>
            </View>
          </View>
        </View>
      </ScrollView>
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
  content: {
    flex: 1,
  },
  statusCard: {
    backgroundColor: '#fff',
    padding: 20,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 24,
    gap: 8,
    marginBottom: 12,
  },
  statusText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  statusDescription: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  qrSection: {
    backgroundColor: '#fff',
    padding: 32,
    alignItems: 'center',
    marginBottom: 16,
  },
  qrContainer: {
    padding: 16,
    backgroundColor: '#fff',
    borderRadius: 16,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    marginBottom: 16,
  },
  qrCode: {
    fontSize: 14,
    color: '#666',
    fontFamily: 'monospace',
  },
  section: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  infoCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  eventName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#666',
  },
  itemsCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  orderItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  itemName: {
    fontSize: 16,
    color: '#333',
  },
  itemPrice: {
    fontSize: 16,
    fontWeight: '600',
    color: '#6200ee',
  },
  summaryCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  summaryLabel: {
    fontSize: 14,
    color: '#666',
  },
  summaryValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  totalRow: {
    marginTop: 8,
    paddingTop: 12,
    borderTopWidth: 2,
    borderTopColor: '#e0e0e0',
  },
  totalLabel: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  totalValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#6200ee',
  },
});