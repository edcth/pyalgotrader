from vnpy.trader.constant import Offset, Direction
from vnpy.trader.object import TradeData, OrderData, TickData
from vnpy.trader.engine import BaseEngine

from vnpy.app.algo_trading import AlgoTemplate


class StopAlgo(AlgoTemplate):
    """"""

    display_name = "Stop  to delegate "

    default_setting = {
        "vt_symbol": "",
        "direction": [Direction.LONG.value, Direction.SHORT.value],
        "stop_price": 0.0,
        "volume": 0.0,
        "price_add": 0.0,
        "offset": [
            Offset.NONE.value,
            Offset.OPEN.value,
            Offset.CLOSE.value,
            Offset.CLOSETODAY.value,
            Offset.CLOSEYESTERDAY.value
        ]
    }

    variables = [
        "traded",
        "vt_orderid",
        "order_status",
    ]

    def __init__(
        self,
        algo_engine: BaseEngine,
        algo_name: str,
        setting: dict
    ):
        """"""
        super().__init__(algo_engine, algo_name, setting)

        # Parameters
        self.vt_symbol = setting["vt_symbol"]
        self.direction = Direction(setting["direction"])
        self.stop_price = setting["stop_price"]
        self.volume = setting["volume"]
        self.price_add = setting["price_add"]
        self.offset = Offset(setting["offset"])

        # Variables
        self.vt_orderid = ""
        self.traded = 0
        self.order_status = ""

        self.subscribe(self.vt_symbol)
        self.put_parameters_event()
        self.put_variables_event()

    def on_tick(self, tick: TickData):
        """"""
        if self.vt_orderid:
            return

        if self.direction == Direction.LONG:
            if tick.last_price >= self.stop_price:
                price = self.stop_price + self.price_add

                if tick.limit_up:
                    price = min(price, tick.limit_up)

                self.vt_orderid = self.buy(
                    self.vt_symbol,
                    price,
                    self.volume,
                    offset=self.offset
                )
                self.write_log(
                    f" stop order has been triggered ， code ：{self.vt_symbol}， direction ：{self.direction},  price ：{self.stop_price}， quantity ：{self.volume}， kaiping ：{self.offset}")

        else:
            if tick.last_price <= self.stop_price:
                price = self.stop_price - self.price_add

                if tick.limit_down:
                    price = max(price, tick.limit_down)

                self.vt_orderid = self.sell(
                    self.vt_symbol,
                    price,
                    self.volume,
                    offset=self.offset
                )
                self.write_log(
                    f" stop order has been triggered ， code ：{self.vt_symbol}， direction ：{self.direction},  price ：{self.stop_price}， quantity ：{self.volume}， kaiping ：{self.offset}")

        self.put_variables_event()

    def on_order(self, order: OrderData):
        """"""
        self.traded = order.traded
        self.order_status = order.status

        if not order.is_active():
            self.stop()
        self.put_variables_event()

    def on_trade(self, trade: TradeData):
        """"""
        pass