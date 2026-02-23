import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import { useCart } from '../../contexts/CartContext';
import { Ionicons } from '@expo/vector-icons';
import Constants from 'expo-constants';

const API_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL;

export default function CheckoutScreen() {
  const { id } = useLocalSearchParams();
  const [useCredits, setUseCredits] = useState(0);
  const [loading, setLoading] = useState(false);
  const { token, user, updateUser } = useAuth();
  const { items, getTotal, clearCart } = useCart();
  const router = useRouter();

  const subtotal = getTotal();
  const platformFee = subtotal * 0.10;
  const creditsToUse = Math.min(useCredits, user?.credits || 0, subtotal + platformFee);
  const total = subtotal + platformFee - creditsToUse;

  const handlePayment = async () => {
    if (items.length === 0) {
      Alert.alert('Erro', 'Carrinho vazio');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          event_id: id,
          items: items,
          use_credits: creditsToUse,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Erro ao processar pedido');
      }

      // Update user credits
      if (user && creditsToUse > 0) {
        updateUser({ ...user, credits: user.credits - creditsToUse });
      }

      clearCart();
      Alert.alert('Sucesso!', 'Pedido realizado com sucesso!', [
        {
          text: 'Ver Pedido',
          onPress: () => router.replace(`/order/${data.id}`),
        },
      ]);
    } catch (error: any) {
      Alert.alert('Erro', error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Finalizar Pedido</Text>
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Resumo do Pedido</Text>
          {items.map((item) => (
            <View key={item.product_id} style={styles.orderItem}>
              <Text style={styles.itemName}>
                {item.quantity}x {item.product_name}
              </Text>
              <Text style={styles.itemPrice}>
                R$ {(item.unit_price * item.quantity).toFixed(2)}
              </Text>
            </View>
          ))}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Pagamento</Text>
          <View style={styles.paymentCard}>
            <View style={styles.paymentInfo}>
              <Ionicons name="card" size={32} color="#6200ee" />
              <View style={styles.paymentText}>
                <Text style={styles.paymentMethod}>Pagamento Mockado</Text>
                <Text style={styles.paymentDescription}>
                  O pagamento é simulado para demonstração
                </Text>
              </View>
            </View>
          </View>
        </View>

        {user && user.credits > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Usar Créditos</Text>
            <View style={styles.creditsCard}>
              <View style={styles.creditsInfo}>
                <Ionicons name="wallet" size={24} color="#6200ee" />
                <Text style={styles.creditsAvailable}>
                  Disponível: R$ {user.credits.toFixed(2)}
                </Text>
              </View>
              <View style={styles.creditsInput}>
                <Text style={styles.creditsLabel}>Usar créditos:</Text>
                <TextInput
                  style={styles.input}
                  keyboardType="numeric"
                  placeholder="0.00"
                  value={useCredits.toString()}
                  onChangeText={(text) => {
                    const value = parseFloat(text) || 0;
                    setUseCredits(value);
                  }}
                />
              </View>
              <TouchableOpacity
                style={styles.useAllCreditsButton}
                onPress={() => setUseCredits(Math.min(user.credits, subtotal + platformFee))}
              >
                <Text style={styles.useAllCreditsText}>Usar todos os créditos</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Resumo de Valores</Text>
          <View style={styles.summaryCard}>
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Subtotal</Text>
              <Text style={styles.summaryValue}>R$ {subtotal.toFixed(2)}</Text>
            </View>
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Taxa da plataforma (10%)</Text>
              <Text style={styles.summaryValue}>R$ {platformFee.toFixed(2)}</Text>
            </View>
            {creditsToUse > 0 && (
              <View style={styles.summaryRow}>
                <Text style={[styles.summaryLabel, { color: '#4caf50' }]}>Créditos usados</Text>
                <Text style={[styles.summaryValue, { color: '#4caf50' }]}>
                  - R$ {creditsToUse.toFixed(2)}
                </Text>
              </View>
            )}
            <View style={[styles.summaryRow, styles.totalRow]}>
              <Text style={styles.totalLabel}>Total a pagar</Text>
              <Text style={styles.totalValue}>R$ {total.toFixed(2)}</Text>
            </View>
          </View>
        </View>
      </ScrollView>

      <View style={styles.footer}>
        <TouchableOpacity
          style={[styles.payButton, loading && styles.payButtonDisabled]}
          onPress={handlePayment}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Ionicons name="checkmark-circle" size={24} color="#fff" />
              <Text style={styles.payButtonText}>Confirmar Pagamento</Text>
            </>
          )}
        </TouchableOpacity>
      </View>
    </View>
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
  section: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
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
  paymentCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  paymentInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  paymentText: {
    marginLeft: 16,
    flex: 1,
  },
  paymentMethod: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  paymentDescription: {
    fontSize: 14,
    color: '#666',
  },
  creditsCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  creditsInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  creditsAvailable: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#6200ee',
    marginLeft: 12,
  },
  creditsInput: {
    marginBottom: 12,
  },
  creditsLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#f9f9f9',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  useAllCreditsButton: {
    padding: 12,
    backgroundColor: '#f0e6ff',
    borderRadius: 8,
    alignItems: 'center',
  },
  useAllCreditsText: {
    color: '#6200ee',
    fontWeight: 'bold',
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
  footer: {
    padding: 16,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  payButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#6200ee',
    padding: 16,
    borderRadius: 12,
    gap: 8,
  },
  payButtonDisabled: {
    opacity: 0.6,
  },
  payButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});