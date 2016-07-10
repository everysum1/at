def find_marked_candles(charts):
    chart_id_candle_map = {}

    for chart in charts:
        chart_id = chart['id']
        candles = chart['candles']
        patterned_candles = [candle for candle in candles if candle.get('pattern')]
        chart_id_candle_map[chart_id] = patterned_candles

    return chart_id_candle_map


def find_chart_start_end_date(candles):
    sorted_candles = sorted(candles, key=lambda t: t['date']['utc'])

    start = sorted_candles[0]['date']['utc']
    end = sorted_candles[-1]['date']['utc']

    return start, end


def find_target_candle(target_candle, date_id_map):
    print 'TARGET_CANDLE', target_candle
    print('NUM candles', len(date_id_map))
    target_date = target_candle['date']
    try:
        matching_candle = date_id_map[target_date]
    except KeyError as e:
        print('e', e)
        return None
    return matching_candle


def make_date_id_map(candles, hours_offset):
    date_id_map = {}

    for candle in candles:
        date = candle['date']

        old_formatted_date = '-'.join([str(date['year']), str(date['month']), str(date['day']), str(date['hour']),
                                       str(date['minute'])])

        old_hours = int(date['hour'])
        old_days = int(date['day'])
        hours_offset = -8
        new_hours = old_hours + hours_offset

        if new_hours < 0:
            hours = 24 - abs(new_hours)
            days = old_days - 1
        else:
            hours = new_hours
            days = old_days

        new_formatted_date = '-'.join([str(date['year']), str(date['month']), str(days), str(hours),
                                       str(date['minute'])])

        print(old_formatted_date, new_formatted_date)

        date_id_map[new_formatted_date] = candle

    return date_id_map
