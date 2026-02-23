import React, { createContext, useContext, useState } from 'react';

interface CartItem {
  product_id: string;
  product_name: string;
  quantity: number;
  unit_price: number;
}

interface CartContextData {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
  getTotal: () => number;
}

const CartContext = createContext<CartContextData>({} as CartContextData);

export const CartProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [items, setItems] = useState<CartItem[]>([]);

  const addItem = (item: CartItem) => {
    const existingItem = items.find(i => i.product_id === item.product_id);
    
    if (existingItem) {
      setItems(items.map(i => 
        i.product_id === item.product_id 
          ? { ...i, quantity: i.quantity + item.quantity }
          : i
      ));
    } else {
      setItems([...items, item]);
    }
  };

  const removeItem = (productId: string) => {
    setItems(items.filter(item => item.product_id !== productId));
  };

  const updateQuantity = (productId: string, quantity: number) => {
    if (quantity <= 0) {
      removeItem(productId);
    } else {
      setItems(items.map(item => 
        item.product_id === productId ? { ...item, quantity } : item
      ));
    }
  };

  const clearCart = () => {
    setItems([]);
  };

  const getTotal = () => {
    return items.reduce((total, item) => total + (item.unit_price * item.quantity), 0);
  };

  return (
    <CartContext.Provider value={{ items, addItem, removeItem, updateQuantity, clearCart, getTotal }}>
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => useContext(CartContext);