import streamlit as st

class Logistics_fee:
    def __init__(self, shipping_rate):
        self.shipping_rate = shipping_rate

    def volumetric_weight_calculator(self, l, w, d):
        vlm_wgt = float(l*w*d/6000*1000)
        return vlm_wgt

    def chargable_weight_calculator(self, l, w, d, gross_weight, volumetric_weight, threshold=40):
        if max(l, w, d) < threshold:
            chargable_weight = gross_weight
        elif max(l, w, d) >= threshold and volumetric_weight <= gross_weight*1.3:
            chargable_weight = gross_weight
        else:
            chargable_weight = gross_weight + (volumetric_weight - gross_weight*1.3)
        return chargable_weight

    def register_fee_calculator(self, chargable_weight):
        if 0 < chargable_weight <= 100:
            register_fee = 24
        elif 101 <= chargable_weight <= 200:
            register_fee = 25
        elif 201 <= chargable_weight <= 450:
            register_fee = 28
        elif 451 <= chargable_weight <= 31500:
            register_fee = 39
        else:
            register_fee = 39
        return register_fee

    def deliver_fee_calculator(self, chargable_weight):
        deliver_fee = float(chargable_weight/1000)*self.shipping_rate
        return deliver_fee
    
class NetSales:
    def __init__(self, sales_price, final_value_fee_rate = 0.136, international_fee_rate = 0.0165):
            self.sales_price = sales_price
            self.final_value_fee_rate = final_value_fee_rate
            self.international_fee_rate = international_fee_rate
            self.transaction_fee = self.transaction_fee_calculator()

    def transaction_fee_calculator(self):
        if self.sales_price < 0:
            raise ValueError("Sales price should be greater than 0")
        elif self.sales_price < 10:
            transaction_fee = 0.3
        else:
            transaction_fee = 0.4
        return transaction_fee
    
    def net_sales_calculator(self):
         net_sales = self.sales_price*(1 - self.final_value_fee_rate - self.international_fee_rate) - self.transaction_fee
         return net_sales, self.sales_price*self.final_value_fee_rate, self.sales_price*self.international_fee_rate, self.transaction_fee

if __name__ == "__main__":
    st.set_page_config(page_title="Arthur Liu 利润计算器", layout="wide")
    st.title('📊 Arthur Liu 的利润成本计算器(侧边栏改数)')
    st.markdown("---")

    # --- SIDEBAR INPUTS ---
    with st.sidebar:
        st.header('📦 物品规格')
        length = st.number_input("长 (cm):", value=10.0)
        width = st.number_input("宽 (cm):", value=10.0)
        height = st.number_input("高 (cm):", value=10.0)
        weight = st.number_input("毛重 (g):", value=500.0)

        st.header('💰 财务设置')
        price = st.number_input("物品定价 (USD):", value=25.0)
        product_cost = st.number_input('产品成本 (CNY):', value=10.0)
        exchange_rate = st.number_input('人民币汇美元汇率:', value=7.2)
        
        # Hardcoded shipping rate as per your logic, or we could make it an input
        shipping_rate_val = 138 
        st.caption(f"当前默认物流单价: {shipping_rate_val} CNY/kg")

    # --- LOGIC EXECUTION ---
    logistics = Logistics_fee(shipping_rate=shipping_rate_val)
    ns_instance = NetSales(price)
    
    net_sales_usd, fvf, int_fee, trans_fee = ns_instance.net_sales_calculator()
    total_fee_usd = fvf + int_fee + trans_fee
    
    volumetric_weight = logistics.volumetric_weight_calculator(length, width, height)
    chargable_weight = logistics.chargable_weight_calculator(length, width, height, weight, volumetric_weight)
    register_fee = logistics.register_fee_calculator(chargable_weight)
    deliver_fee = logistics.deliver_fee_calculator(chargable_weight)
    total_cost_logistics = deliver_fee + register_fee
    
    actual_income_cny = net_sales_usd * exchange_rate
    profit_cny = actual_income_cny - product_cost - total_cost_logistics
    

    # --- UI POLISHING START ---

    # Row 1: Key Metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader('🚚 物流详情')
        st.info(f"""
        - **毛重:** {weight} g
        - **体积重:** {volumetric_weight:.2f} g
        - **挂号费:** ¥{register_fee:.2f}
        - **快递费:** ¥{deliver_fee:.2f}
        - **包材费用:** ¥0.00
        - **总物流支出:** ¥{(deliver_fee+register_fee):.2f}
        """)

    with col2:
        st.subheader('🏢 平台 & 成本')
        st.warning(f"""
        - **产品成本:** ¥{product_cost:.2f}
        - **汇率:** {exchange_rate}
        - **FVF (佣金):** ${fvf:.2f}
        - **FVF (佣金):** ¥{exchange_rate*fvf:.2f}
        - **国际手续费:** ${int_fee:.2f}
        - **国际手续费:** ¥{exchange_rate*int_fee:.2f}
        - **Transaction Fee:** ${trans_fee:.2f}
        - **Transaction Fee:** ¥{exchange_rate*trans_fee:.2f}
        - **平台费&产品总成本:** ¥{product_cost+exchange_rate*fvf+exchange_rate*int_fee+exchange_rate*trans_fee:.2f}
        """)

    with col3:
        st.subheader('💰 利润总结')
        st.info(f"""
        - **售价:**${price:.2f})
        - **售价:**¥{price*exchange_rate:.2f}
        - **实际到账收入:** ¥{actual_income_cny:.2f}
        - **物流+产品成本项:** ¥{product_cost + total_cost_logistics:.2f}
        """)
        
        st.divider()
        if profit_cny >= 0:
            st.success(f"### 净利润: ¥{profit_cny:.2f}")
            st.success(f'### 净利润% {profit_cny/(price*exchange_rate)*100:.2f}')
        else:
            st.error(f"### 净亏损: ¥{profit_cny:.2f}")

    st.divider()