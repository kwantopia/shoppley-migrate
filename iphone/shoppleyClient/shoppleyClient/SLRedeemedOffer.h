//
//  SLRedeemedOffer.h
//  shoppleyClient
//
//  Created by yod on 6/18/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "SLOffer.h"

@interface SLRedeemedOffer : SLOffer {
    
}

@property (nonatomic, retain) NSString* redeemedOn;

+ (NSArray*)offersArrayfromDictionary:(NSDictionary*)data;

- (void)populateFromDictionary:(NSDictionary*)data;

@end

@interface SLRedeemedOfferTableItem : TTTableLinkedItem {
    SLRedeemedOffer* _offer;
}

@property(nonatomic,retain) SLRedeemedOffer* offer;

+ (id)itemWithOffer:(SLRedeemedOffer*)offer URL:(NSString*)URL;

@end
