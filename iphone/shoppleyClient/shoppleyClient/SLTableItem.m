//
//  SLTableItem.m
//  shoppleyClient
//
//  Created by yod on 6/18/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLTableItem.h"


@implementation SLRightValueTableItem

+ (id)itemWithText:(NSString*)text value:(NSString*)value {
    SLRightValueTableItem* item = [[[self alloc] init] autorelease];
    item.text = text;
    item.caption = value;
    return item;
}

@end

@implementation SLStarsTableItem

@synthesize numberOfStars = _numberOfStars;

+ (id)itemWithNumberofStars:(NSNumber*)numberOfStars {
    SLStarsTableItem* item = [[[self alloc] init] autorelease];
    item.numberOfStars = numberOfStars;
    return item;
}

- (void)dealloc {
    TT_RELEASE_SAFELY(_numberOfStars);
    [super dealloc];
}

- (id)initWithCoder:(NSCoder*)decoder {
    if ((self = [super initWithCoder:decoder])) {
        self.numberOfStars = [decoder decodeObjectForKey:@"numberOfStars"];
    }
    return self;
}

- (void)encodeWithCoder:(NSCoder*)encoder {
    [super encodeWithCoder:encoder];
    if (self.numberOfStars) {
        [encoder encodeObject:self.numberOfStars forKey:@"numberOfStars"];
    }
}

@end
