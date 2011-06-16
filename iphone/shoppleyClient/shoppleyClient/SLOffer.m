//
//  SLOffer.m
//  shoppleyClient
//
//  Created by yod on 6/14/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLOffer.h"


@implementation SLOffer
@synthesize name, description, code, img, phone, lat, lon;

- (void)populateFromDictionary:(NSDictionary*)data {
    self.name = [data objectForKey:@"name"];
    self.description = [data objectForKey:@"description"];
    self.code = [data objectForKey:@"code"];
    self.img = [data objectForKey:@"img"];
    self.phone = [data objectForKey:@"phone"];
    self.lat = [data objectForKey:@"lat"];
    self.lon = [data objectForKey:@"lon"];
}

@end
