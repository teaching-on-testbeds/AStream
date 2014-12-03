""" Adaptation algorithm
"""
import config_dash


def calculate_rate_index(bitrates, curr_rate):
    """ Module that finds the birate closes to the curr_rate
    :param bitrates: LIst of available bitrates
    :param curr_rate: current_bitrate
    :return: curr_rate_index
    """
    if curr_rate < bitrates[0]:
        return bitrates[0]
    elif curr_rate > bitrates[-1]:
        return bitrates[-1]
    else:
        for bitrate, index in enumerate(bitrates[1:]):
            if bitrates[index-1] < curr_rate < bitrate:
                return curr_rate


def basic_dash(segment_number, bitrates, average_dwn_time,
               segment_download_time, curr_rate):
    """
    :param segment_number: Current segment number
    :param bitrates: A tuple/list of available bitrates
    :param average_dwn_time: Average download time observed so far
    :param segment_download_time:  Time taken to download the current segment
    :param curr_rate: Current bitrate being used
    :return: next_rate : Bitrate for the next segment
    :return: updated_dwn_time: Updated average downlaod time
    """

    if average_dwn_time > 0 and segment_number > 0:
        updated_dwn_time = (average_dwn_time * (segment_number + 1) + segment_download_time) / (segment_number + 1)
    else:
        updated_dwn_time = segment_download_time
    config_dash.LOG.debug("The average download time upto segment {} is {}. Before it was {}".format(segment_number,
                                                                                                     updated_dwn_time,
                                                                                                     average_dwn_time))
    segment_download_time = float(segment_download_time)
    bitrates = [float(i) for i in bitrates]
    bitrates.sort()
    try:
        sigma_download = average_dwn_time / segment_download_time
        config_dash.LOG.debug("Sigma Download = {}/{} = {}".format(average_dwn_time, segment_download_time, sigma_download))
    except ZeroDivisionError:
        config_dash.LOG.error("Download time = 0. Unable to calculate the sigma_download")
        return curr_rate, updated_dwn_time
    try:
        curr = bitrates.index(curr_rate)
    except ValueError:
        config_dash.LOG.error("Current Bitrate not in the bitrate lsit. Setting to minimum")
        curr = calculate_rate_index(bitrates, curr_rate)
    next_rate = curr_rate
    if sigma_download < 1:
        if curr > 0:
            if sigma_download < bitrates[curr - 1]/bitrates[curr]:
                next_rate = bitrates[0]
            else:
                next_rate = bitrates[curr - 1]
    elif curr_rate < bitrates[-1]:
        if sigma_download >= bitrates[curr - 1]/bitrates[curr]:
            temp_index = curr
            while next_rate < bitrates[-1] or sigma_download < (bitrates[curr+1] / bitrates[curr]):
                temp_index += 1
                next_rate = bitrates[temp_index]
    return next_rate, updated_dwn_time
