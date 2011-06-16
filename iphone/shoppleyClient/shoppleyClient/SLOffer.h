//
//  SLOffer.h
//  shoppleyClient
//
//  Created by yod on 6/14/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>


@interface SLOffer : NSObject {

}

@property (nonatomic, retain) NSString* name;
@property (nonatomic, retain) NSString* description;
@property (nonatomic, retain) NSString* code;
@property (nonatomic, retain) NSString* img;
@property (nonatomic, retain) NSString* phone;
@property (nonatomic, retain) NSNumber* lat;
@property (nonatomic, retain) NSNumber* lon;

- (void)populateFromDictionary:(NSDictionary*)data;

@end
