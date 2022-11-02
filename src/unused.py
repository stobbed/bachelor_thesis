# (CC) Dustin Stobbe, 2022

# database_operations.py
def close_db_connection(sqliteConnection, cursor):
    if (sqliteConnection):
            cursor.close()
            sqliteConnection.close()
            print('The SQLite connection is closed')


# db.py
# class Db
def create_dict_event_id_links(self) -> "dict":
    """ reads all vehicle_link_events from DB and stores this information with the event_id as key in a dictionary """
    return get_links_for_event_id(self._cursor, self.event_id_link_dict, self.link_information_dict)

def create_driven_links_dict(self, vehicleslist: list) -> "dict":
    """ creates a dictionary with vehicle id as key for a list of trips as content. each trip contains the necessary informtion, when the vehicle entered and left the link, the length and freespeed """
    create_entered_link_dict(vehicleslist, self.event_id_link_dict, self.driven_links_dict, self._cursor)
    return self.driven_links_dict

def calculate_passenger_occupancy(self, drtvehicleids: list) -> "dict":
    """ retrieves information about pickup_dropoff events from DB and stores the passenger amount for each event_id where such an event happened in a dictionary """
    return get_passenger_occupancy(drtvehicleids, self._cursor)

def calculate_passengers_for_link(self, drtvehicleids: list, dictofPassengerOccupancy: dict, driven_links_dict: dict) -> "dict":
    """ uses the previously created dictionary dictofPassengerOccupancy to retrieve how many passengers where in the car and stores that information based on the links (connected by the event_id) in a dictionary """
    return get_passengers_for_link(drtvehicleids, dictofPassengerOccupancy, driven_links_dict, self._cursor)

def assign_capacity(self, drtvehicleids: list, vehicledict: dict):
    """ looks up capacity for each vehicle id in vehicleids in DB and returns capacity and adds it in the vehicledict """
    return get_capacity(drtvehicleids, vehicledict, self._cursor)

def get_vehicle_entered_links(self,ids) -> "LinksForEvent":
    create_dict_entered_links(ids, self._cursor,self.entered_dict)
    return self.entered_dict

def get_vehicle_left_links(self,ids) -> "LinksForEvent":
    create_dict_left_links(ids, self._cursor,self.left_dict)
    return self.left_dict

def get_link(self, event_id):
    return self.event_id_link_dict[event_id]

def get_time(self, event_id):
    return get_time_for_event_id(event_id, self._cursor)

# no class
class MockDb:  
    def get_vehicles(self):
        return ["bmw","vw"]

    def get_vehicle_links(self,ids):
        d = LinksForEvent()
        d.add("bmw",[Trip("zittauer","1"),Trip("berliner","2")])
        # d.add("vw","456")
        return d

def test_get_occ():
    db = MockDb()
    events = db.get_traffic_events()
    asssert 
def test_get_road_perc():
    trips = [Trip('baker street',0),Trip('berliner allee',50)]
    velocities = {"baker street": 50.}
    city,land,autobahn  = get_road_perc(trips,velocities)
    assert city == .5
    assert land == .5
    assert autobahn == 0.


# processing.py
def get_passengers_for_link(vehicle: str, passengeroccupancy: list, driven_links: list, cursor: sqlite3.Cursor) -> "dict":
    """ uses the previously created dictionary dictofPassengerOccupancy to retrieve how many passengers where in the car and stores that information based on the links (connected by the event_id) in a dictionary"""
    # print("adding passengers to each trip in driven_links_dict...")
    for index in range(0, len(passengeroccupancy)):
        link_for_task = get_link_for_dvrpTask_event(passengeroccupancy[index], vehicle, cursor)
        if index != len(passengeroccupancy)-1:
            link_for_next_task = get_link_for_dvrpTask_event(passengeroccupancy[index+1], vehicle, cursor)
        else:
            link_for_next_task = None
        # if db_output == []:
        #     db_output = query_db(query, cursor, id, time[0][0]+1)
        start = False
        stop = False
        for tripindex in range(0, len(driven_links)):
            trip = driven_links[tripindex]
            if trip.link == link_for_task and start == False and stop == False:
                # print(id, db_output[0][0])
                start = True
            if link_for_next_task != None:
                if trip.link == link_for_next_task and stop == False:
                    stop = True
            if start == True and stop == False:
                driven_links[tripindex].passengers = passengeroccupancy[index][1]
    # print("...succesfully added passengers to all trips!")
    return driven_links

def create_dict_vid_distance_roadpct(dictofVIDandLinks, dictofLinks_Length, dictofLinks_Freespeed, drtvehicleids):
    print("creating dictionaries with VID and distance, as well as roadpct...")
    dictofVIDandDistance = {}
    dictofVIDandRoadPct = defaultdict(list)

    in_town_max = 51 / 3.6
    out_town_max = 101 / 3.6

    for id in drtvehicleids:
        dictofVIDandDistance[id] = 0
        roadpctlist = []
        roadpctlist.append(0)
        roadpctlist.append(0)
        roadpctlist.append(0)
        for links in dictofVIDandLinks[id]:
            dictofVIDandDistance[id] += dictofLinks_Length[str(links)]
            if dictofLinks_Freespeed[str(links)] <= in_town_max:
                roadpctlist[0] += dictofLinks_Length[str(links)]
            if dictofLinks_Freespeed[str(links)] <= out_town_max and dictofLinks_Freespeed[str(links)] > in_town_max:
                roadpctlist[1] += dictofLinks_Length[str(links)]
            if dictofLinks_Freespeed[str(links)] > out_town_max:
                roadpctlist[2] += dictofLinks_Length[str(links)]
        roadpctlist[0] = roadpctlist[0]/dictofVIDandDistance[id]
        roadpctlist[1] = roadpctlist[1]/dictofVIDandDistance[id]
        roadpctlist[2] = roadpctlist[2]/dictofVIDandDistance[id]
        dictofVIDandRoadPct[id] = roadpctlist
    return dictofVIDandRoadPct, dictofVIDandDistance

def create_dict_linkinformation(cursor):
    print("creating dictionaries with link ids, length and freespeed...")
    query = ''' SELECT link_id, length, freespeed FROM network_links '''
    linkslist_fromdb = query_db(query, cursor)

    dictofLinks_Length = {}
    dictofLinks_Freespeed = {}
    for tuple in linkslist_fromdb:
        key = tuple[0]
        dictofLinks_Length[key] = tuple[1]
        dictofLinks_Freespeed[key] = tuple[2]
    print("successfully created dictionaries with link ids, length and freespeed")
    return dictofLinks_Length, dictofLinks_Freespeed

def create_dict_entered_links(drtvehicleids, cursor, linkdict):
    print("creating dictionary with driven links for each VID")
    query = '''     SELECT l.link, l.event_id, e.time, n.length, n.freespeed
                    FROM (enteredlink_events l INNER JOIN events e ON e.event_id == l.event_id)
                    INNER JOIN network_links n ON l.link == n.link_id
                    WHERE vehicle = ?'''
    for id in drtvehicleids:
        linkdict.add(id, get_links_for_VID(id, query, cursor))
    print("successfully created dictionary with VID and links")

def create_dict_left_links(drtvehicleids, cursor, linkdict):
    print("creating dictionary with driven links for each VID")
    query = '''     SELECT l.link, l.event_id, e.time, n.length, n.freespeed
                    FROM (leftlink_events l INNER JOIN events e ON e.event_id == l.event_id)
                    INNER JOIN network_links n ON l.link == n.link_id
                    WHERE vehicle = ?'''
    for id in drtvehicleids:
        linkdict.add(id, get_links_for_VID(id, query, cursor))
    print("successfully created dictionary with VID and links")

def get_links_for_VID(id, query, cursor) -> "list[Trip]":
    db_output = query_db(query, cursor, id)
    res = []
    for tuple in db_output:
        link = tuple[0]
        event_id = tuple[1]
        entered_time = tuple[2]
        link_length = tuple[3]
        link_freespeed = tuple[4]
        res.append(Trip(link, event_id, entered_time,
                   link_length, link_freespeed))
    return res

def get_speeds_for_link_and_id(enteredlinks, leftlinks, vehicleslist, cursor):
    for id in vehicleslist:
        i = 0
        triplist = enteredlinks.d[id]
        for trip in triplist:
            link = trip.link
            lefttripslist = leftlinks.d[id]
            z = 0
            for lefttrip in lefttripslist:
                if lefttrip.link == link and z >= i-5 and z <= i+5:
                    enteredlinks.d[id][i].left_time = lefttrip.entered_time
                    print(enteredlinks.d[id][i].entered_time)
                    print(enteredlinks.d[id][i].left_time)
                    print(link)
                    print(lefttrip.link)
                z += 1
            if enteredlinks.d[id][i].left_time > enteredlinks.d[id][i].entered_time:
                enteredlinks.d[id][i].actual_speed = enteredlinks.d[id][i].link_length / (enteredlinks.d[id][i].left_time - enteredlinks.d[id][i].entered_time)
                enteredlinks.d[id][i].speed_pct = enteredlinks.d[id][i].actual_speed / enteredlinks.d[id][i].link_freespeed
                if enteredlinks.d[id][i].speed_pct < .2:
                    times = get_time_for_dvrpTask(id, link, cursor)
                    if times != None:
                        for time in times:
                            if time >= enteredlinks.d[id][i].entered_time and time <= enteredlinks.d[id][i].left_time:
                                print('vehicle: ' + str(id) + ' time match entered: ' + str(enteredlinks.d[id][i].entered_time) + ' left: ' + str(enteredlinks.d[id][i].left_time) + ' and stopped at: ' + str(time) + ' on link: ' + str(link))
                                print(i)
                                print(z)
                    # print('speed pct: ' + str(enteredlinks.d[id][i].speed_pct) + ' on link: ' + str(enteredlinks.d[id][i].link) + ' for vehicle: ' + str(id))
                    # print('actual speed: ' + str(enteredlinks.d[id][i].actual_speed))
                    # print('link speed: ' + str(enteredlinks.d[id][i].link_freespeed))
            else:
                pass
                # print('no left time, or does not make sense on: ' + str(enteredlinks.d[id][i].link))
            i += 1

def get_speeds_for_link_and_id(enteredlinks, leftlinks, vehicleslist, cursor):
    for id in vehicleslist:
        i = 0
        triplist = enteredlinks.d[id]
        for trip in triplist:
            link = trip.link
            lefttripslist = leftlinks.d[id]
            z = 0
            for index in range(i, len(lefttripslist)):
                if index >= i:
                    lefttrip = lefttripslist[index]
                    if lefttrip.link == link and enteredlinks.d[id][i].left_time == -1:
                        enteredlinks.d[id][i].left_time = lefttrip.entered_time
                        # print(index)
                        # print(i)
                        # print(enteredlinks.d[id][i].entered_time)
                        # print(enteredlinks.d[id][i].left_time)
                        # print(link)
                        # print(lefttrip.link)
            if enteredlinks.d[id][i].left_time > enteredlinks.d[id][i].entered_time:
                enteredlinks.d[id][i].actual_speed = enteredlinks.d[id][i].link_length / (enteredlinks.d[id][i].left_time - enteredlinks.d[id][i].entered_time)
                enteredlinks.d[id][i].speed_pct = enteredlinks.d[id][i].actual_speed / enteredlinks.d[id][i].link_freespeed
                if enteredlinks.d[id][i].speed_pct < .2:
                    times = get_time_for_dvrpTask(id, link, cursor)
                    if times != None:
                        for time in times:
                            if time >= enteredlinks.d[id][i].entered_time and time <= enteredlinks.d[id][i].left_time:
                                print('vehicle: ' + str(id) + ' time match entered: ' + str(enteredlinks.d[id][i].entered_time) + ' left: ' + str(enteredlinks.d[id][i].left_time) + ' and stopped at: ' + str(time) + ' on link: ' + str(link))
                                print(i)
                    # print('speed pct: ' + str(enteredlinks.d[id][i].speed_pct) + ' on link: ' + str(enteredlinks.d[id][i].link) + ' for vehicle: ' + str(id))
                    # print('actual speed: ' + str(enteredlinks.d[id][i].actual_speed))
                    # print('link speed: ' + str(enteredlinks.d[id][i].link_freespeed))
            else:
                pass
                # print('no left time, or does not make sense on: ' + str(enteredlinks.d[id][i].link))
            i += 1

def get_speed(vehicleslist, cursor):
    for id in vehicleslist:
        get_links_entered_and_left_for_VID(id, cursor)

def get_time_for_dvrpTask(vehicleid, link, cursor):
    query = '''     SELECT e.time
                    FROM dvrpTask_events d INNER JOIN events e ON e.event_id == d.event_id
                    WHERE d.dvrpVehicle = ? AND d.link = ? AND d.taskType = ?'''
    taskType = 'STAY'
    db_output = query_db(query, cursor, vehicleid, link, taskType)
    time = []
    for tuple in db_output:
        for entry in tuple:
            time.append(entry)
    if time != []:
        return time

def get_links_entered_and_left_for_VID(id, cursor):
    # query = ''' SELECT e.event_id, e.time, type_id, v.link
    #             FROM events e INNER JOIN vehicle_link_events v on v.event_id == e.event_id
    #             WHERE e.vehicle = ? '''
    query = ''' SELECT event_id, time, type_id
                FROM events
                WHERE vehicle = ? '''
    db_output = query_db(query, cursor, id)
    print(id)
    for index in range(0, len(db_output)):
        event_id = db_output[index][0]
        time = db_output[index][1]
        type_id = db_output[index][2]
        # link = db_output[index][3]
        if type_id == 7 or type_id == 8:
            pass
        else:
            print(event_id, time, type_id)

def get_links_for_event_id(cursor, event_id_link_dict: dict, link_information_dict: dict) -> "dict":
    """ reads all vehicle_link_events from DB and stores this information with the event_id as key in a dictionary"""
    print("creating event_id_link_dict..." + str(gettime()))
    query = ''' SELECT event_id, link, left_entered
                FROM vehicle_link_events '''
    db_output = query_db(query, cursor)
    # iterate through db_output list of tuples and store information contained in tuple in dictionary with event_id as key
    # and store the information contained in the link_information_dict for this link as well
    for tuple in db_output:
        event_id = tuple [0]
        link = tuple [1]
        left_entered = tuple [2]
        # retrieve information for link from link_information_dict
        length = link_information_dict[str(link)].length
        freespeed = link_information_dict[str(link)].freespeed
        event_id_link_dict[event_id] = Links(link, length, freespeed, left_entered)
    print("...succesfully created event_id_link_dict!" + str(gettime()))
    return event_id_link_dict

def create_entered_link_dict(vehicleslist: list, event_id_link_dict: dict, driven_links_dict: dict, cursor) -> dict:
    """ creates a dictionary with vehicle id as key for a list of trips as content. 
        each trip contains the necessary informtion, when the vehicle entered and left the link, the length and freespeed
        this script als calculates the actual speeed, as well as the percentual speed it therefore reached"""
    print("creating entered_link_dict..." + str(gettime()))
    for id in vehicleslist:
        query = ''' SELECT event_id, time, type_id, vehicle
                FROM events 
                WHERE vehicle = ?'''
        db_output = query_db(query, cursor, id)
        driven_links_dict.d[id] = []
        tripindex = 0
        # iterate through db_output with an index
        for index in range(0, len(db_output)):
            event_id = db_output[index][0]
            time = db_output[index][1]
            type_id = db_output[index][2]
            vehicle = db_output[index][3]
            # type_id == 8 means entered link and therefore appends the dictionary with the Class trip and its information
            if type_id == 8:
                trip = event_id_link_dict[event_id]
                link = trip.link
                length = trip.length
                freespeed = trip.freespeed
                driven_links_dict.d[vehicle].append(Trip(link, event_id, time, length, freespeed))
                tripindex += 1
            # type_id == 7 means left link
            elif type_id == 7:
                # checks if its the first interaction of the car, since then there could be no entered link before that
                if tripindex != 0:
                    # if the previous event of the car was entering this particular link, stores 
                    if db_output[index-1][2] == 8 and driven_links_dict.d[vehicle][tripindex-1].link == event_id_link_dict[event_id].link:
                        entered_index = tripindex -1
                        driven_links_dict.d[vehicle][entered_index].left_time = time
                        driven_links_dict.d[vehicle][entered_index].actual_speed = driven_links_dict.d[vehicle][entered_index].link_length/(time - driven_links_dict.d[vehicle][entered_index].entered_time)
                        driven_links_dict.d[vehicle][entered_index].speed_pct = driven_links_dict.d[vehicle][entered_index].actual_speed/driven_links_dict.d[vehicle][entered_index].link_freespeed
            # type_id == 4 means vehicle enters traffic, therefore further calculation is required
            elif type_id == 4 and db_output[index+1][2] == 7:
                stop1 = False
                stop2 = False
                index_entered_link = index
                index_left_link = index + 1
                index_entered_traffic = index
                index_left_traffic = index
                # search for an event prior to entering traffic where the vehicle entered the link and storing its index
                while db_output[index_entered_link][2] != 8 and stop1 == False:
                    # stop condition, so index always stays above 0
                    if index_entered_link == 1:
                        stop1 = True
                    index_entered_link -= 1
                # search for an event prior to entering traffic, where the vehicle left traffic and store its index
                while db_output[index_left_traffic][2] != 9 and stop2 == False:
                    # stop condition, so index always stays above 0
                    if index_left_traffic== 1:
                        stop2 = True
                    index_left_traffic -= 1
                query = ''' SELECT link FROM vehicle_traffic_events WHERE event_id = ?'''
                # if index for left_traffic was found and is not 0...
                if index_left_traffic != 0:
                    # looks up the link for the event_id corresponding to the entered and left traffic events
                    link_entered_traffic = query_db(query, cursor, db_output[index_entered_traffic][0])[0]
                    link_left_traffic = query_db(query, cursor, db_output[index_left_traffic][0])[0]
                    # checks if links are a match and then calculates the time spent outside of traffic and only uses time on link for speed calculation
                    if event_id_link_dict[db_output[index_entered_link][0]].link == link_entered_traffic[0] and link_left_traffic[0] == link_entered_traffic[0] and event_id_link_dict[db_output[index_entered_link][0]].link == event_id_link_dict[db_output[index_left_link][0]].link:
                        time_spent_outside_traffic = db_output[index_entered_traffic][1] - db_output[index_left_traffic][1]
                        time_difference = db_output[index_left_traffic][1] - db_output[index_entered_link][1] + db_output[index_left_link][1] - db_output[index_entered_traffic][1]
                        left_time_corrected = db_output[index_left_link][1] - time_spent_outside_traffic
                        i = 0
                        # due to setting the driven_links_dict up as a list, a search for the index matching the event_id where the link was entered is necessary
                        for trip in driven_links_dict.d[id]:
                            if trip.event_id == db_output[index_entered_link][0]:
                                index_entered_link_corrected = i
                            i += 1
                        driven_links_dict.d[vehicle][index_entered_link_corrected].left_time = left_time_corrected
                        driven_links_dict.d[vehicle][index_entered_link_corrected].actual_speed = driven_links_dict.d[vehicle][index_entered_link_corrected].link_length/(left_time_corrected - driven_links_dict.d[vehicle][index_entered_link_corrected].entered_time)
                        driven_links_dict.d[vehicle][index_entered_link_corrected].speed_pct = driven_links_dict.d[vehicle][index_entered_link_corrected].actual_speed/driven_links_dict.d[vehicle][index_entered_link_corrected].link_freespeed
                        driven_links_dict.d[vehicle][index_entered_link_corrected].corrected = True
    print("...succesfully created entered_link_dict!" + str(gettime())

def vehicle_enters_traffic_event(event_id_link_dict, driven_links_dict, db_output, vehicle, index, cursor):
    stop1 = False
    stop2 = False
    index_entered_link = index
    index_left_link = index + 1
    index_entered_traffic = index
    index_left_traffic = index
    while db_output[index_entered_link][2] != 8 and stop1 == False:
        if index_entered_link == 1:
            stop1 = True
        index_entered_link -= 1
    while db_output[index_left_traffic][2] != 9 and stop2 == False:
        if index_left_traffic== 1:
            stop2 = True
        index_left_traffic -= 1
        query = ''' SELECT link FROM vehicle_traffic_events WHERE event_id = ?'''
        if index_left_traffic != 0:
            link_entered_traffic = query_db(query, cursor, db_output[index_entered_traffic][0])[0]
            link_left_traffic = query_db(query, cursor, db_output[index_left_traffic][0])[0]
            if event_id_link_dict[db_output[index_entered_link][0]].link == link_entered_traffic[0] and link_left_traffic[0] == link_entered_traffic[0] and event_id_link_dict[db_output[index_entered_link][0]].link == event_id_link_dict[db_output[index_left_link][0]].link:
                time_spent_outside_traffic = db_output[index_entered_traffic][1] - db_output[index_left_traffic][1]
                time_difference = db_output[index_left_traffic][1] - db_output[index_entered_link][1] + db_output[index_left_link][1] - db_output[index_entered_traffic][1]
                left_time_corrected = db_output[index_left_link][1] - time_spent_outside_traffic
                i = 0
                for trip in driven_links_dict.d[id]:
                    if trip.event_id == db_output[index_entered_link][0]:
                        index_entered_link_corrected = i
                    i += 1
                driven_links_dict.d[vehicle][index_entered_link_corrected].actual_speed = driven_links_dict.d[vehicle][index_entered_link_corrected].link_length/(left_time_corrected - driven_links_dict.d[vehicle][index_entered_link_corrected].entered_time)
                driven_links_dict.d[vehicle][index_entered_link_corrected].speed_pct = driven_links_dict.d[vehicle][index_entered_link_corrected].actual_speed/driven_links_dict.d[vehicle][index_entered_link_corrected].link_freespeed
                driven_links_dict.d[vehicle][index_entered_link_corrected].corrected = True

def create_vehicle_dict(vehicleids: list, driven_links_dict: dict) -> "dict":
    """ creates a dictionary for each vehicle in vehicleids containing travelleddistance, road percentages as well as pkm and avgpassenger amounts"""
    print("Creating vehicle dictionary...")
    vehicledict = {}
    for id in vehicleids:
        vehicledict[id] = calculate_distance_roadpct(id, driven_links_dict.gettrips(id))
    print("..succesfully created vehicle dictionary")
    return vehicledict

def get_passenger_occupancy(drtvehicleids: list, cursor) -> "dict":
    """ retrieves information about pickup_dropoff events from DB and stores the passenger amount for each event_id where such an event happened in a dictionary"""
    print("creating dictionary with occupancy for event_ids...")
    occupancy_query = '''SELECT event_id, person, request, pickup_dropoff FROM PassengerPickedUpDropOff_events WHERE vehicle = ?'''
    # drivenlinks_query = '''SELECT event_id, link, vehicle FROM enteredlink_events'''
    # db_output_links = query_db(drivenlinks_query, cursor)
    dictofPassengerOccupancy = defaultdict(list)
    for id in drtvehicleids:
        db_output_occupancy = query_db(occupancy_query, cursor, id)
        passengers = 0
        for tuple in db_output_occupancy:
            if tuple[3] == 0:
                # if tuple[3] == 0 means that a passenger was picked up and therfore increases the passenger amount by 1
                passengers += 1
            elif tuple[3] == 1:
                # if tuple[3] == 1 means that a passenger was dropped off and therfore decreases the passenger amount by 1
                passengers -= 1
            # creates a tuple containg the event_id where the pickup_dropff event occured, passengers at that time, as well as the drt request
            occupancytuple = (tuple[0], passengers, tuple[2])
            dictofPassengerOccupancy[id].append(occupancytuple)
    print("...created occupancy dictionary!")
    return dictofPassengerOccupancy

def get_passengers_for_link(drtvehicleids: list, dictofPassengerOccupancy: dict, driven_links_dict: dict, cursor) -> "dict":
    """ uses the previously created dictionary dictofPassengerOccupancy to retrieve how many passengers where in the car and stores that information based on the links (connected by the event_id) in a dictionary"""
    print("adding passengers to each trip in driven_links_dict...")
    for id in drtvehicleids:
        for index in range(0, len(dictofPassengerOccupancy[id])):
            link_for_task = get_link_for_dvrpTask_event(dictofPassengerOccupancy[id][index], id, cursor)
            if index != len(dictofPassengerOccupancy[id])-1:
                link_for_next_task = get_link_for_dvrpTask_event(dictofPassengerOccupancy[id][index+1], id, cursor)
            else:
                link_for_next_task = None
            # if db_output == []:
            #     db_output = query_db(query, cursor, id, time[0][0]+1)
            start = False
            stop = False
            for tripindex in range(0, len(driven_links_dict.d[id])):
                trip = driven_links_dict.d[id][tripindex]
                if trip.link == link_for_task and start == False and stop == False:
                    # print(id, db_output[0][0])
                    start = True
                if link_for_next_task != None:
                    if trip.link == link_for_next_task and stop == False:
                        stop = True
                if start == True and stop == False:
                    driven_links_dict.d[id][tripindex].passengers = dictofPassengerOccupancy[id][index][1]
    print("...succesfully added passengers to all trips!")
    return driven_links_dict

def analyse_speed_pct_threshold(vehicleslist: list, driven_links_dict: dict, speed_pct_threshold = .2):
    """ this function can be used to analyse what amount of the total trips falls below a certain speed_pct_threshold"""
    error = {}
    sumtrips = 0
    sumerror = 0
    for id in vehicleslist:
        counter = 0
        for trip in driven_links_dict.d[id]:
            # this can be used to determine a more detailed analysis
            # if trip.corrected == False and trip.actual_speed == -1 or trip.speed_pct < speed_pct_threshold:
            #     counter += 1
            if trip.speed_pct < speed_pct_threshold:
                counter += 1
        error[id] = [len(driven_links_dict.d[id]), counter]
        sumtrips += len(driven_links_dict.d[id])
        sumerror += counter
    # hier noch anständige Auswertung, mit 10,20....90.. Prozenz
    print('total of: ' + str(sumtrips) + ' trips, with ' + str(sumerror) + ' trips below the threshold of: ' + str(speed_pct_threshold) + ', which results in a percentage of: ' + str(sumerror/ sumtrips))

def create_fleet_information(vehicledict: dict, vehiclelist: list) -> "Fleet":
    """ creates an item of the Class Fleet which contains all the information for the fleet consisting of the vehicles in vehicleslist.
        calculates fleetdistance, distance and pkm for different road types, as well as the biggest distance with roadpcts"""
    print("creating fleet information...")
    fleetdistance = 0
    total_pkm = 0
    distance_intown = 0
    pkm_intown = 0
    distance_countryroad = 0
    pkm_countryroad = 0
    distance_highway = 0
    pkm_highway = 0
    maximum_distance = 0
    # iterare for every vehicle in vehiclelist
    for id in vehiclelist:
        fleetdistance += vehicledict[id].traveleddistance
        distance_intown += vehicledict[id].traveleddistance * vehicledict[id].intown_pct
        pkm_intown += vehicledict[id].pkm_intown
        distance_countryroad += vehicledict[id].traveleddistance * vehicledict[id].countryroad_pct
        pkm_countryroad += vehicledict[id].pkm_countryroad
        distance_highway += vehicledict[id].traveleddistance * vehicledict[id].highway_pct
        pkm_highway += vehicledict[id].pkm_highway
        # checks for the biggest travel distance and stores it in the variable maximum_distance
        if vehicledict[id].traveleddistance > maximum_distance:
            maximum_distance = vehicledict[id].traveleddistance
            roadpct = []
            roadpct.append(vehicledict[id].intown_pct)
            roadpct.append(vehicledict[id].countryroad_pct)
            roadpct.append(vehicledict[id].highway_pct)
    total_pkm = pkm_intown + pkm_countryroad + pkm_highway
    avg_distance = fleetdistance / len(vehiclelist)
    print("...created fleet information")
    return Fleet(vehicledict, fleetdistance, total_pkm, avg_distance, distance_intown, pkm_intown, distance_countryroad, pkm_countryroad, distance_highway, pkm_highway, maximum_distance, roadpct)

def calculate_avg_vehicle(path):
    drt_vehicleamount = 0
    drt_totalkm = 0; drt_totalkm_region = 0; drt_totalkm_notregion = 0; drt_totalpkm = 0
    drt_intown_pct = 0; drt_countryroad_pct = 0; drt_highway_pct = 0
    drt_pkm_intown = 0; drt_pkm_countryroad = 0; drt_pkm_highway = 0
    drt_avg_speed = 0; drt_speed_pct = 0; drt_speed_length = 0; drt_speed_above_90 = 0; drt_speed_below_70 = 0; drt_speed_below_50 = 0; drt_speed_below_30 = 0; drt_speed_below_10 = 0
    drt_avgpassenger_amount = 0; drt_avgpassenger_without_empty = 0; drt_pkm_without_empty = 0

    vehicleamount = 0
    totalkm = 0
    intown_pct = 0; countryroad_pct = 0; highway_pct = 0
    avg_speed = 0; speed_pct = 0; speed_length = 0; speed_above_90 = 0; speed_below_70 = 0; speed_below_50 = 0; speed_below_30 = 0; speed_below_10 = 0
    
    small_vehicles = 0; medium_vehicles = 0; large_vehicles = 0
    # avgpassenger_without_empty = 0
    # data = pd.read_csv("/Users/dstobbe/Downloads/MATSIM Output/hundekopf-rebalancing-1000vehicles-2seats/hundekopf-rebalancing-1000vehicles-2seats_vehicleinfo.csv")
    data = pd.read_csv(os.path.join(path, 'results', getsimulationname(path) + '_vehicleinfo_finished.csv'), low_memory=False, header=0, skip_blank_lines=True)
    # vehicleamount = data._values.shape[0]
    for line in data._values:
        if line[22] == 2:
            small_vehicles += 1
        elif line[22] == 4:
            medium_vehicles += 1
        elif line[22] == 7:
            large_vehicles += 1
        if str(line[0]).startswith("drt") or str(line[0]).startswith("taxi"):
            drt_vehicleamount += 1
            drt_totalkm += line[1]; drt_totalkm_region += line[21]; drt_totalkm_notregion += line[20]; drt_totalpkm += line[8]
            drt_intown_pct += line[2]; drt_countryroad_pct += line[3]; drt_highway_pct += line[4]
            drt_pkm_intown += line[5]; drt_pkm_countryroad += line[6]; drt_pkm_highway += line[7]
            drt_avg_speed += line[12]; drt_speed_pct += line[13]; drt_speed_length += line[14]; drt_speed_above_90 += line[15]; drt_speed_below_70 += line[16]; drt_speed_below_50 += line[17]; drt_speed_below_30 += line[18]; drt_speed_below_10 += line[19]
            drt_avgpassenger_amount += line[9]; drt_avgpassenger_without_empty += line[10]; drt_pkm_without_empty += line[11]
        else:
            if line[1] > 0:
                vehicleamount += 1
                totalkm += line[1]
                intown_pct += line[2]; countryroad_pct += line[3]; highway_pct += line[4]
                avg_speed += line[12]; speed_pct += line[13]; speed_length += line[14]; speed_above_90 += line[15]; speed_below_70 += line[16]; speed_below_50 += line[17]; speed_below_30 += line[18]; speed_below_10 += line[19]
            if totalkm > 0:
                pass
            else: 
                # print(line[1])
                # print(type(line[1]))
                break
    info = {}
    info['drt_vehicleamount'] = drt_vehicleamount
    if drt_vehicleamount > 0:
        info['drt_avg_totalkm_region'] = drt_totalkm_region / drt_vehicleamount
        info['drt_avg_totalkm_notregion'] = drt_totalkm_notregion / drt_vehicleamount
        info['drt_totalkm'] = drt_totalkm
        info['drt_avg_totalkm'] = (drt_totalkm_region + drt_totalkm_notregion) / drt_vehicleamount
        info['drt_avg_totalpkm'] = drt_totalpkm / drt_vehicleamount
        info['drt_avg_intown_pct'] = drt_intown_pct / drt_vehicleamount
        info['drt_avg_countryroad_pct'] = drt_countryroad_pct / drt_vehicleamount
        info['drt_avg_highway_pct'] = drt_highway_pct / drt_vehicleamount
        info['drt_avg_pkm_intown'] = drt_pkm_intown / drt_vehicleamount
        info['drt_avg_pkm_countryroad'] = drt_pkm_countryroad / drt_vehicleamount
        info['drt_avg_pkm_highway'] = drt_pkm_highway / drt_vehicleamount
        info['drt_avg_speed_pervehicle'] = drt_avg_speed / drt_vehicleamount
        info['drt_avg_speed_overlength'] = drt_speed_length / drt_totalkm_region
        info['drt_avg_speed_pct'] = drt_speed_pct / drt_vehicleamount
        info['drt_avg_speed_above_90'] = drt_speed_above_90 / (drt_totalkm_region + drt_totalkm_notregion)
        info['drt_avg_speed_below_70'] = drt_speed_below_70 / (drt_totalkm_region + drt_totalkm_notregion)
        info['drt_avg_speed_below_50'] = drt_speed_below_50 / (drt_totalkm_region + drt_totalkm_notregion)
        info['drt_avg_speed_below_30'] = drt_speed_below_30 / (drt_totalkm_region + drt_totalkm_notregion)
        info['drt_avg_speed_below_10'] = drt_speed_below_10 / (drt_totalkm_region + drt_totalkm_notregion)
        info['drt_avg_passenger_amount'] = drt_avgpassenger_amount / drt_vehicleamount
        info['drt_avgpassenger_without_empty'] = drt_avgpassenger_without_empty / drt_vehicleamount
        info['drt_pkm_without_empty'] = drt_pkm_without_empty / drt_vehicleamount

        info['small_vehicles'] = small_vehicles
        info['medium_vehicles'] = medium_vehicles
        info['large_vehicles'] = large_vehicles

    info['vehicleamount'] = vehicleamount
    info['totalkm'] = totalkm
    info['avg_totalkm'] = totalkm / vehicleamount
    info['avg_intown_pct'] = intown_pct / vehicleamount
    info['avg_countryroad_pct'] = countryroad_pct / vehicleamount
    info['avg_highway_pct'] = highway_pct / vehicleamount
    info['avg_speed_pervehicle'] = avg_speed / vehicleamount
    info['avg_speed_overlength'] = speed_length / totalkm
    info['avg_speed_pct'] = speed_pct / vehicleamount
    info['avg_speed_above_90'] = speed_above_90 / totalkm
    info['avg_speed_below_70'] = speed_below_70 / totalkm
    info['avg_speed_below_50'] = speed_below_50 / totalkm
    info['avg_speed_below_30'] = speed_below_30 / totalkm
    info['avg_speed_below_10'] = speed_below_10 / totalkm
    return info

def create_vehicle_list(path):
    xmlpath = os.path.join(path, getsimulationname(path) + '.output_allVehicles.xml.gz')
    if os.path.exists(xmlpath):
        print('opening xml.gz file...')
        file = gzip.open(xmlpath, mode='rt', encoding='UTF-8')
        print('file opened!')
    else:
        raise FileNotFoundError('Invalid path (xmlpath): '+xmlpath+' - *.xml.gz file doesn\'t exist.')

    tree = ET.parse(file)
    root = tree.getroot()

    vehicles = []
    for child in root:
        if len(child.attrib) > 1:
            if child.attrib['type'] == "car":
                vehicles.append(child.attrib['id'])
    return vehicles
