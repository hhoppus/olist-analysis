--
-- PostgreSQL database dump
--

-- Dumped from database version 16.5
-- Dumped by pg_dump version 16.5

-- Started on 2025-01-20 09:31:15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 4851 (class 1262 OID 33091)
-- Name: olist_db; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE olist_db WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'English_United States.1252';


ALTER DATABASE olist_db OWNER TO postgres;

\connect olist_db

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 215 (class 1259 OID 33122)
-- Name: customers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customers (
    customer_id text,
    customer_unique_id text,
    customer_zip_code_prefix text,
    customer_city text,
    customer_state text
);


ALTER TABLE public.customers OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 33140)
-- Name: order_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_items (
    order_id text,
    order_item_id text,
    product_id text,
    seller_id text,
    shipping_limit_date text,
    price text,
    freight_value text
);


ALTER TABLE public.order_items OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 33171)
-- Name: order_payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_payments (
    order_id text,
    payment_sequential text,
    payment_type text,
    payment_installments text,
    payment_value text
);


ALTER TABLE public.order_payments OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 33150)
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    order_id text,
    customer_id text,
    order_status text,
    order_purchase_timestamp text,
    order_approved_at text,
    order_delivered_carrier_date text,
    order_delivered_customer_date text,
    order_estimated_delivery_date text
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 33165)
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    product_id text,
    product_category_name text,
    product_name_length text,
    product_description_length text,
    product_photos_qty text,
    product_weight_g text,
    product_length_cm text,
    product_height_cm text,
    product_width_cm text
);


ALTER TABLE public.products OWNER TO postgres;

-- Completed on 2025-01-20 09:31:15

--
-- PostgreSQL database dump complete
--

