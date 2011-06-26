//
//  SLTableItem.m
//  shoppleyMerchant
//
//  Created by yod on 6/18/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLTableItem.h"


@implementation SLRightValueTableItem

+ (id)itemWithText:(NSString*)text value:(NSString*)value {
    return [self itemWithText:text value:value URL:nil];
}

+ (id)itemWithText:(NSString*)text value:(NSString*)value URL:(NSString *)URL {
    SLRightValueTableItem* item = [[[self alloc] init] autorelease];
    item.text = text;
    item.caption = value;
    item.URL = URL;
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

@implementation SLRightStarsTableItem
@synthesize numberOfStars = _numberOfStars;

+ (id)itemWithText:(NSString*)text numberOfStars:(NSNumber*)numberOfStars URL:(NSString *)URL {
    SLRightStarsTableItem* item = [[[self alloc] init] autorelease];
    item.text = text;
    item.numberOfStars = numberOfStars;
    item.URL = URL;
    return item;
}

@end
